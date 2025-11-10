#!/usr/bin/env python3
# Updated version of stopwrdz.py that removes punctuation from subtitle text lines
# without affecting SRT timecodes or numbering lines.  It also skips empty
# subtitle lines produced after punctuation removal.  This script is based off
# the original TrustViking/Stopwrdz version.

from os.path import split, join, splitext
from typing import List, Optional, Dict, Union
from io import BytesIO
import re

from app_env.decorators import safe_execute
from app_env.systems_methods import SysMethods
from app_env.filtering_vocab import Filtering
from app_env.reading import Reading
from app_env.saving import Saving
from app_env.cleaning import Cleaning
from app_env.base_class import BaseClass


class Start(BaseClass):
    """
    Module for START.  This class orchestrates reading an SRT file, selecting
    the appropriate vocabulary based on detected language, replacing stop words,
    and writing out a new SRT file.  Punctuation characters are stripped from
    subtitle lines (but not from timecode lines) prior to replacement, and
    subtitle lines which become empty after punctuation removal are omitted
    from the output.
    """
    countInstance = 0

    def __init__(self) -> None:
        super().__init__()
        Start.countInstance += 1
        self.countInstance = Start.countInstance

        # переопределяем родительский атрибут cls_name
        self.cls_name = self.__class__.__name__
        # читаем конфигурацию
        self.config = self.read_config(self.config_path)
        self.replace_dict = self.config.get('replace_dictionary')
        # self.punct = self.config.get('punct')
        self.new_name_title = self.config.get('new_name_title')

        # инициализируем вспомогательные классы
        self.sysmethods = SysMethods()
        self.srt_file = self.sysmethods.args()  # путь к файлу титров
        self.reading = Reading()
        self.saving = Saving()
        self.cleaning = Cleaning()
        self.filtering = Filtering()

    def string_disassembled(self, line: str, diction: Dict[str, str]) -> Optional[str]:
        """
        Разбирает строку на слова, заменяет стоп‑слова и возвращает
        строку без знаков пунктуации.  Время и номера кадров не должны
        обрабатываться этим методом.

        Parameters
        ----------
        line : str
            Входная строка для обработки.
        diction : Dict[str, str]
            Словарь для замены стоп‑слов.

        Returns
        -------
        Optional[str]
            Строка после удаления пунктуации и замены стоп‑слов, либо
            None в случае исключения.
        """
        name_method = self.get_current_method_name()

        @safe_execute(
            logger=self.logger,
            name_method=f'[{self.cls_name}|{name_method}]',
        )
        def _string_disassembled() -> Optional[str]:
            """
            Удаляет пунктуацию и «умные» тире/дефисы из входной строки,
            затем выполняет замену стоп‑слов.

            Основные правила:
            * Любые знаки пунктуации (категория Unicode P*) удаляются.
            * Все варианты тире/дефисов (короткое/длинное, неразрывный, минус и т.п.)
              удаляются, если они стоят в окружении пробелов или не являются частью слова.
              Тире/дефис сохраняется только в том случае, если по обе стороны от него
              находятся буквы без пробелов (пример: «как‑нибудь», «word‑processing»).
            * После удаления символов строка разбивается на слова.  Каждое слово
              заменяется по словарю `diction`.
            * Определён набор исключений пунктуации (`punct_exceptions`), которые сохраняются
              и не удаляются (например, знак процента `%`).
            * Если после удаления пунктуации и замен по словарю в строке не осталось слов,
              возвращается строка-заглушка `'00000'`.  Это позволяет выделить пустые блоки
              титров, чтобы затем их было легко найти и удалить вручную. Такая строка
              не считается ошибкой.
            """
            import unicodedata

            # Набор символов пунктуации, которые мы не хотим удалять.
            # Легко редактировать и расширять в будущем.
            punct_exceptions = {
                '%',  # знак процента должен сохраняться
                "'",  # ASCII apostrophe (английский апостроф)
                '’',  # U+2019: типографский апостроф, часто используется в украинском тексте
                'ʼ',  # U+02BC: украинский апостроф
            }
            # Набор символов, рассматриваемых как тире/дефис/минус.
            dash_chars = {
                '-',        # U+002D: ASCII hyphen-minus
                '‐',        # U+2010: hyphen
                '‑',        # U+2011: non-breaking hyphen
                '‒',        # U+2012: figure dash
                '–',        # U+2013: en dash
                '—',        # U+2014: em dash
                '―',        # U+2015: horizontal bar
                '−',        # U+2212: minus sign
                '⁃'         # U+2043: hyphen bullet
            }

            # строка-заглушка для пустых строк
            placeholder_string = '00000'

            s = line
            out_chars: List[str] = []
            n = len(s)

            # локальная функция для проверки, является ли символ буквой
            def is_letter(char: str) -> bool:
                return char.isalpha()
            # локальная функция для проверки, является ли символ буквой или цифрой
            def is_word_char(char: str) -> bool:
                return char.isalnum()


            for i, char in enumerate(s):
                prev_char = s[i - 1] if i > 0 else ''
                next_char = s[i + 1] if i + 1 < n else ''

                if char in dash_chars:
                    # сохраняем дефис/тире только если он между буквами или цифрами без пробелов
                    if is_word_char(prev_char) and is_word_char(next_char) and prev_char != ' ' and next_char != ' ':
                        out_chars.append('-')  # нормализуем на простой дефис
                    # иначе — игнорируем (не добавляем)
                    continue

                # фильтрация остальных символов пунктуации
                cat = unicodedata.category(char)
                # пропускаем символы пунктуации, если они не исключены
                if cat.startswith('P') and char not in punct_exceptions:
                    continue  # пропускаем пунктуационные символы

                out_chars.append(char)

            # Собранная строка без пунктуации и лишних тире
            line_no_punct = ''.join(out_chars)

            # Разбиваем на слова (убираем лишние пробелы)
            words_raw = line_no_punct.split()
            # Если после удаления пунктуации не осталось слов, возвращаем строку-заглушку
            # Это сигнал тому, что строку нужно обратить внимание и, при необходимости,
            # удалить вручную. Используем пять нулей для удобства поиска.
            if not words_raw:
                return placeholder_string

            # Замена каждого слова по словарю
            replaced_words = [diction.get(w, w) for w in words_raw]
            result = ' '.join(replaced_words)
            # Если после замен строка стала пустой, также возвращаем строку-заглушку
            # (пять нулей), чтобы можно было легко найти и удалить при пост-обработке.
            if not result.strip():
                return placeholder_string
            return result

        return _string_disassembled()

    def replace_swords_buffer(
        self,
        buf: Union[str, List[str], BytesIO],
        diction: Dict[str, str],
        # punctuation: List[str],
    ) -> Optional[List[str]]:
        """
        Заменяет стоп‑слова в буфере строк.  Таймкоды и номера кадров
        оставляются без изменений.  Пустые строки исходного файла сохраняются.
        Линии субтитров, ставшие пустыми после удаления пунктуации, исключаются.
        """
        name_method = self.get_current_method_name()

        # определяем источник буфера в список строк
        if isinstance(buf, str):
            buf_lines = buf.split('\n')
        elif isinstance(buf, list):
            buf_lines = buf
        elif isinstance(buf, BytesIO):
            buf.seek(0)
            buf_lines = [line.decode('utf-8') for line in buf.readlines()]
        else:
            buf_lines = []

        new_buf: List[str] = []
        # регулярное выражение для определения строки‑таймкода
        timecode_re = re.compile(r'^\d{2}:\d{2}:\d{2},\d{3}\s+-->')

        for i, line in enumerate(buf_lines):
            stripped = line.strip()
            # сохраняем пустые строки, номера кадров и таймкоды без изменений
            if stripped == '' or stripped.isdigit() or timecode_re.match(stripped):
                new_buf.append(line)
                continue
            # обрабатываем только текстовые строки
            string_after_replace = self.string_disassembled(line, diction)
            if string_after_replace is None:
                msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не смогли обработать строку № {i} на предмет замены стоп‑слов'
                    f'\n*string_after_replace: [{string_after_replace}]'
                )
                print(msg)
                self.logger.error(msg)
                return None
            # пропускаем строки, ставшие пустыми после удаления пунктуации
            if string_after_replace.strip() == '':
                continue
            new_buf.append(string_after_replace)

        return new_buf

    def process_title( 
        self,
        file_path: str,
        replace_dict: Dict[str, str],
        # punctuation: List[str],
        nfile: str,
    ) -> Optional[str]:
        """
        Обрабатывает файл титров, заменяя стоп‑слова и сохраняя
        изменения в новом файле.
        """
        name_method = self.get_current_method_name()

        # определяем кодировку файла
        encoding = self.reading.encoding_file(file_path)
        if not encoding:
            msg = (
                f'\n*ERROR [{self.cls_name}|{name_method}]'
                f'\n*Не определили кодировку файла титров'
            )
            print(msg)
            self.logger.error(msg)
            return None

        # читаем файл в список строк
        buffer_title = self.reading.read_file_to_buffer_lines(file_path, encoding)
        if not buffer_title:
            msg = (
                f'\n*ERROR [{self.cls_name}|{name_method}]'
                f'\n*Не прочитали файл титров с диска в память'
            )
            print(msg)
            self.logger.error(msg)
            return None

        # выбираем и подготавливаем словарь стоп‑слов
        swords = self.filtering.training_vocab(buffer_title, replace_dict)
        if not swords:
            msg = (
                f'\n*ERROR [{self.cls_name}|{name_method}]'
                f'\n*Не создали словарь стоп‑слов: {swords}'
            )
            print(msg)
            self.logger.error(msg)
            return None

        # заменяем стоп‑слова в буфере
        new_buf = self.replace_swords_buffer(buffer_title, swords)
        if not new_buf:
            msg = (
                f'\n*ERROR [{self.cls_name}|{name_method}]'
                f'\n*Не создали новый буфер файла титров {new_buf}'
            )
            print(msg)
            self.logger.error(msg)
            return None

        # формируем уникальный путь для нового файла
        directory, filename = split(file_path)
        language = self.filtering.last_detected_language
        if language:
            base_name, extension = splitext(nfile)
            # если в конфигурации не указано расширение, используем исходное имя как есть
            if extension:
                nfile = f"{base_name}_{language}{extension}"
            else:
                nfile = f"{nfile}_{language}"

        new_full_path_title = join(directory, nfile)
        new_uniq_full_path_title = self.saving.get_unique_file_path(new_full_path_title)
        full_path_saving_title = self.saving.save_buffer_disk(
            new_uniq_full_path_title, new_buf
        )
        return full_path_saving_title


def main() -> None:
    # создаём экземпляр класса Start
    start = Start()
    name_method = start.get_current_method_name()
    print(f"\n[{start.cls_name}|{name_method}]\nStart...")

    full_path_title = start.srt_file
    replace_dictionary = start.replace_dict
    # punctuation = start.punct
    new_name_title = start.new_name_title
    config_path = start.config_path

    # удаляем старые лог‑файлы
    print(
        f'Всего удалили [{start.cleaning.delete_logs(config_path)}] старых файлов журналов логгов'
    )

    # выполняем основной скрипт
    full_path_saving_title = start.process_title(
        full_path_title, replace_dictionary, new_name_title
    )
    if not full_path_saving_title:
        msg = (
            f'\n*ERROR [{name_method}|{start.cls_name}]'
            f'\n*Не создали новый файл титров'
            f'\n*full_path_saving_title {full_path_saving_title}'
        )
        print(msg)
        start.logger.error(msg)
    else:
        msg = (
            f'\n# [{name_method}|{start.cls_name}]'
            f'\n# Cоздали новый файл титров'
            f'\n# full_path_saving_title {full_path_saving_title}'
        )
        print(msg)

    input("\nНажмите клавишу <Enter> для выхода...")


if __name__ == "__main__":
    main()
