#!/usr/bin/env python3
#
import shutil
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex 
from pynvml import nvmlDeviceGetMemoryInfo, nvmlShutdown
from psutil import virtual_memory
from logging import getLevelName
from time import strftime
from os.path import getmtime, isdir, isfile, split, splitext
from os.path import basename, join, abspath, dirname, exists 
from os import makedirs, listdir, remove
from sys import platform, argv, path
from typing import Coroutine, List, Optional, Dict, Union
from time import sleep, strftime
from datetime import datetime as dt
import chardet
from io import BytesIO
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

#
from app_env.decorators import safe_execute
from app_env.app_init import LogInitializer, ConfigInitializer
from app_env.systems_methods import SysMethods
from app_env.prints_screen import Prints
from app_env.filtering_vocab import Filtering
from app_env.reading import Reading
from app_env.saving import Saving
from app_env.sys_memory import SysMemory
from app_env.cleaning import Cleaning



class Start(ConfigInitializer):
    """Module for START"""
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Start.countInstance += 1
        self.countInstance = Start.countInstance
        #
        self.abspath = dirname(abspath(__file__))
        self.cls_name = self.__class__.__name__
        # config
        self.config_path = join(dirname(abspath(__file__)), 'config.json')
        self.config = self.read_config(self.config_path)
        self.folder_vocabs = self.config.get('folder_vocabs')
        self.pattern_name_vocab = self.config.get('pattern_name_vocab')
        # ℃ ∈ ☪
        self.replace_dict = self.config.get('replace_dict')
        self.punct = self.config.get('punct')
        self.new_name_title = self.config.get('new_name_title')
        # Logger
        self.log_init = LogInitializer()
        self.logger = self.log_init.initialize(self.config_path)
        
        # Prints
        self.prints = Prints()
        # SysMemory
        self.sysmemory = SysMemory()
        # SysMethods
        self.sysmethods = SysMethods()
        # Reading
        self.reading = Reading()
        # Filtering
        self.filtering = Filtering()
        # Saving
        self.saving = Saving()
        # Cleaning
        self.cleaning = Cleaning()

        ## Путь к файлу титров из командной строки
        self.srt_file = self.sysmethods.args()
        
        # создаем рабочие пути
        self.path_vocab_pattern = join(path[0], self.folder_vocabs, self.pattern_name_vocab)


        self.prints.print_main()
        #
        #     
    
    def string_disassembled(self, 
                            line: str, 
                            diction: Dict[str, str], 
                            punctuation: List[str]) -> Optional[str]:
        """
        Разбирает строку на слова, заменяет стоп-слова и возвращает строку 
        с учетом пунктуации.

        Args:
            self: Экземпляр класса.
            line (str): Входная строка для обработки.
            diction (Dict[str, str]): Словарь для замены стоп-слов.
            punctuation (List[str]): Список знаков пунктуации.

        Returns:
            Optional[str]: Строка после разбора, замены стоп-слов и восстановления пунктуации.
            Возвращает None в случае ошибки.
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _string_disassembled():
            puncts=[] # список кортежей знаков препинания и их порядковый номер в строке
            list_chars_without_punct = [] # список символов строки без знаков препинания
            
            # убираем знаки препинания из строки и запоминаем их расположение
            for i, char in enumerate(line):
                if char in punctuation:
                    puncts.append((i, char))
                else:
                    list_chars_without_punct.append(char)

            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nЗнаки препинания в строке и их расположение'
                    f'\npuncts: {puncts}'
                    )
            print(msg)
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nСписок символов строки без знаков препинания'
                    f'\nlist_chars_without_punct: {list_chars_without_punct}'
                    )
            print(msg)
            
            # строка из списка символов строки без знаков препинания
            new_line = ''.join(list_chars_without_punct)
            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nСтрока из списка символов строки без знаков препинания'
                    f'\nnew_line: {new_line}'
                    )
            print(msg)

            # Разбиваем строку на список слов (по пробелам)
            # Максимальная глубина разбора строки
            words = [word.strip() for word in new_line.split()] 
            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nРазбиваем по пробелам строку на список слов'
                    f'\nwords: {words}'
                    )
            print(msg)
            
            # проверяем каждое слово из строки без знаков препинания на совпадение 
            # в словаре стоп-слов и заменяем его
            new_words = [diction.get(word, word) for word in words]
            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nпроверяем каждое слово из строки без знаков препинания на совпадение в словаре стоп-слов и заменяем его'
                    f'\nnew_words: {new_words}'
                    )
            print(msg)
            
            ## начинаем собирать строку обратно
            # после замены стоп-слов соединяем через пробел список слов в строку
            new_string = ' '.join(new_words)
            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nпосле замены стоп-слов соединяем через пробел список слов в строку'
                    f'\nnew_string: {new_string}'
                    )
            print(msg)

            # строку переводим в список символов
            symbols = list(new_string)
            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nстроку переводим в список символов'
                    f'\nsymbols: {symbols}'
                    )
            print(msg)

            # добавляем в список символов на сохраненные позиции пунктуацию 
            if puncts:
                for i, punct in puncts:
                    symbols.insert(i, punct)
            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nдобавляем в список символов на сохраненные позиции пунктуацию'
                    f'\nsymbols: {symbols}'
                    )
            print(msg)
            
            # список символов с пунктуацией переводим в строку
            string_puncts = ''.join(symbols)
            # debug
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nсписок символов с пунктуацией переводим в строку'
                    f'\nstring_puncts: {string_puncts}'
                    )
            print(msg)
            
            return string_puncts
        return _string_disassembled()


    def replace_swords_buffer(self, 
                              buf: Union[str, List[str], BytesIO], 
                              diction: Dict[str, str], 
                              punctuation: List[str]) -> Optional[List[str]]:
        """
        Заменяет стоп-слова в буфере согласно словарю.

        Args:
            self: Экземпляр класса.
            buf (Union[str, List[str], BytesIO]): Буфер с данными для замены слов. 
                Может быть как строкой, так и списком строк, или BytesIO.
            diction (Dict[str, str]): Словарь, где ключи - слова для замены, 
                                      а значения - заменяющие слова.
            punctuation (List[str]): Список знаков пунктуации.

        Returns:
            Optional[List[str]]: Список строк с замененными словами или None в случае ошибки.
        """            
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _replace_swords_buffer():
            if isinstance(buf, str):
                # Если buf - строка, преобразуем её в список строк
                buf_lines = buf.split('\n')
            elif isinstance(buf, list[str]):
                # Если buf - список строк, оставляем как есть
                buf_lines = buf
            # Если buf - BytesIO
            elif isinstance(buf, BytesIO):
                # позиция курсора в начало буфера
                buf.seek(0)
                buf_lines = [line.decode('utf-8') for line in buf.readlines()]

            new_buf = []
            # Проходим по каждой строке в буфере
            for line in buf_lines:
                # Разбираем строку на слова, заменяем стоп-слова и восстанавливаем пунктуацию                
                string_after_replace = self.string_disassembled(line, diction, punctuation)
                if string_after_replace is None: 
                    msg = (
                            f'\n*ERROR [{__name__}|{self.cls_name}]'
                            f'\n*Не смогли обработать строку на предмет замены стоп-слов'
                            f'\n*string_after_replace: [{string_after_replace}]'
                            )
                    print(msg)
                    self.logger.log_info(msg) 
                    return None 
                 # Добавляем обработанную строку в новый буфер
                new_buf.append(string_after_replace)

            return new_buf
        return _replace_swords_buffer()


    ######
    ## обработчик файла титров
    def process_title(self, 
                      file_path: str,  # Путь к исходному файлу титров
                      path_vocab_pattern: str,  # Шаблон пути к словарю по языкам
                      replace_dict: Dict[str, str],  # Словарь для замены символов
                      punctuation: List[str],  # Список знаков пунктуации
                      nfile: str  # Имя нового файла титров
                      ) -> Optional[str]:  # Возвращает полный путь к новому файлу или None в случае ошибки
        
        """
        Обрабатывает файл титров, заменяя стоп-слова и сохраняя изменения в новом файле.

        Args:
            file_path (str): Путь к исходному файлу титров.
            path_vocab_pattern (str): Шаблон пути к словарю по языкам.
            replace_dict (Dict[str, str]): Словарь для замены символов.
            punctuation (List[str]): Список знаков пунктуации.
            nfile (str): Имя нового файла титров.

        Returns:
            Optional[str]: Полный путь к новому файлу титров, если успешно обработано, 
            иначе None.
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _process_title():
            # Определяет кодировку файла с помощью библиотеки chardet
            encoding = self.reading.encoding_file(file_path)
            if not encoding:
                msg = (
                        f'\n*ERROR [{__name__}|{self.cls_name}]'
                        f'\n*Не определили кодировку файла титров'
                        f'\n*buffer_title: {buffer_title}'
                        )
                print(msg)
                self.logger.log_info(msg) 
                return None 
            
            # Читает файл с диска в буфер памяти в виде списка строк символов
            buffer_title = self.reading.read_file_to_buffer_lines(file_path, encoding)
            if not buffer_title:
                msg = (
                        f'\n*ERROR [{__name__}|{self.cls_name}]'
                        f'\n*Не прочитали файл титров с диска в память'
                        f'\n*buffer_title: {buffer_title}'
                        )
                print(msg)
                self.logger.log_info(msg) 
                return None 
                
            # Выбирает и подготавливает словарь стоп-слов с учетом языка файла титров
            swords = self.filtering.training_vocab(buffer_title, 
                                                   path_vocab_pattern, 
                                                   replace_dict)
            if not swords:
                msg = (
                        f'\n*ERROR [{__name__}|{self.cls_name}]'
                        f'\n*Не создали словарь стоп-слов: {swords}'
                        ) 
                print(msg)
                self.logger.log_info(msg)
                return None
            
            # Заменяет стоп-слова в буфере согласно словарю
            new_buf = self.replace_swords_buffer(buffer_title, swords, punctuation)
            if not new_buf:
                msg = (
                        f'\n*ERROR [{__name__}|{self.cls_name}]'
                        f'\n*Не создали новый буфер файла титров {new_buf}'
                    ) 
                print(msg)
                self.logger.log_info(msg)
                return None
            
            # записываем новый файл титров с замененными стоп-словами
            # nfile='swords_title.srt' # имя файла новых титров
            # Разделение пути на директорию и имя файла
            directory, filename = split(file_path)
            new_full_path_title = join(directory, nfile)
            new_uniq_full_path_title = self.saving.get_unique_file_path(new_full_path_title)
            # Записывает содержимое буфера на диск в соответствии с его типом
            full_path_saving_title = self.saving.save_buffer_disk(new_uniq_full_path_title, new_buf)

            return full_path_saving_title
        return _process_title()



# MAIN **************************
# Главная асинхронная функция
def main():
    # Создаем экземпляр класса Start
    start = Start()
    start.sysmemory.system_status() # выводим состояние системы
    sleep(3)
    start.sysmemory.log_memory() # логирование информации о памяти
    sleep(3)
    msg = (
            f'\n\n[{__name__}|{start.cls_name}]'
            f'\nStart...'
        ) 
    print(msg)
    full_path_title = start.srt_file
    path_vocab_pattern = start.path_vocab_pattern
    replace_dictionary = start.replace_dict
    punctuation = start.punct
    new_name_title = start.new_name_title

    # выполняем основной скрипт
    full_path_saving_title = start.process_title(full_path_title, 
                                                path_vocab_pattern, 
                                                replace_dictionary, 
                                                punctuation, 
                                                new_name_title)
    if not full_path_saving_title:
        msg = (
                f'\n*ERROR [{__name__}|{start.cls_name}]'
                f'\n*Не создали новый файл титров'
                f'\n*full_path_saving_title {full_path_saving_title}'
                ) 
        print(msg)
        start.logger.log_info(msg)

    msg = (
            f'\n# [{__name__}|{start.cls_name}]'
            f'\n# Cоздали новый файл титров'
            f'\n# full_path_saving_title {full_path_saving_title}'
            ) 
    print(msg)
    start.logger.log_info(msg)




# Запускаем главную функцию
if __name__ == "__main__":
    main()



