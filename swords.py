
from os.path import split, join
from typing import List, Optional, Dict, Union
from io import BytesIO

from app_env.decorators import safe_execute
from app_env.systems_methods import SysMethods
from app_env.filtering_vocab import Filtering
from app_env.reading import Reading
from app_env.saving import Saving
from app_env.cleaning import Cleaning
from app_env.base_class import BaseClass
#

class Start(BaseClass):
    """
    Module for START
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Start.countInstance += 1
        self.countInstance = Start.countInstance

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__
        #
        # config
        self.config = self.read_config(self.config_path)
        self.replace_dict = self.config.get('replace_dictionary')
        self.punct = self.config.get('punct')
        self.new_name_title = self.config.get('new_name_title')

        # SysMethods
        self.sysmethods = SysMethods()
        # Путь к файлу титров из командной строки
        self.srt_file = self.sysmethods.args()
        # Reading
        self.reading = Reading()
        # Saving
        self.saving = Saving()
        # Cleaning
        self.cleaning = Cleaning()
        # Filtering
        self.filtering = Filtering()


    def string_disassembled(self, 
                            line: str, 
                            diction: Dict[str, str], 
                            punctuation: List[str]
                            ) -> Optional[str]:
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
        name_method = self.get_current_method_name()
        @safe_execute(logger=self.logger, name_method=f'[{self.cls_name}|{name_method}]')
        def  _string_disassembled():
            puncts=[] # список кортежей знаков препинания и их порядковый номер в строке
            list_chars_without_punct = [] # список символов строки без знаков препинания
            
            # убираем знаки препинания из строки и запоминаем их расположение
            for i, char in enumerate(line):
                if char in punctuation:
                    puncts.append((i, char))
                else:
                    list_chars_without_punct.append(char)

            # строка из списка символов строки без знаков препинания
            new_line = ''.join(list_chars_without_punct)

            # Разбиваем строку на список слов (по пробелам)
            # Максимальная глубина разбора строки
            words = [word.strip() for word in new_line.split()] 
            
            # проверяем каждое слово из строки без знаков препинания на совпадение 
            # в словаре стоп-слов и заменяем его
            new_words = [diction.get(word, word) for word in words]
            
            ## начинаем собирать строку обратно
            # после замены стоп-слов соединяем через пробел список слов в строку
            new_string = ' '.join(new_words)

            # строку переводим в список символов
            symbols = list(new_string)

            # добавляем в список символов на сохраненные позиции пунктуацию 
            if puncts:
                for i, punct in puncts:
                    symbols.insert(i, punct)
            
            # список символов с пунктуацией переводим в строку
            string_puncts = ''.join(symbols)
            
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
        name_method = self.get_current_method_name()

        if isinstance(buf, str):
            # Если buf - строка, преобразуем её в список строк
            buf_lines = buf.split('\n')
        elif isinstance(buf, list):
            # Если buf - список строк, оставляем как есть
            buf_lines = buf
        # Если buf - BytesIO
        elif isinstance(buf, BytesIO):
            # позиция курсора в начало буфера
            buf.seek(0)
            buf_lines = [line.decode('utf-8') for line in buf.readlines()]

        new_buf = []
        # Проходим по каждой строке в буфере
        for i, line in enumerate(buf_lines):
            # Разбираем строку на слова, заменяем стоп-слова и восстанавливаем пунктуацию                
            string_after_replace = self.string_disassembled(line, diction, punctuation)
            if string_after_replace is None: 
                msg = (
                        f'\n*ERROR [{self.cls_name}|{name_method}]'
                        f'\n*Не смогли обработать строку № {i} на предмет замены стоп-слов'
                        f'\n*string_after_replace: [{string_after_replace}]'
                        )
                print(msg)
                self.logger.error(msg)
                return None 
            # Добавляем обработанную строку в новый буфер
            new_buf.append(string_after_replace)

        return new_buf


    ## обработчик файла титров
    def process_title(self, 
                      file_path: str,  # Путь к исходному файлу титров
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

        name_method = self.get_current_method_name()

        # Определяет кодировку файла с помощью библиотеки chardet
        encoding = self.reading.encoding_file(file_path)
        if not encoding:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не определили кодировку файла титров'
                    f'\n*buffer_title: {buffer_title}'
                    )
            print(msg)
            self.logger.error(msg) 
            return None 
        
        # Читает файл с диска в буфер памяти в виде списка строк символов
        buffer_title = self.reading.read_file_to_buffer_lines(file_path, encoding)
        if not buffer_title:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не прочитали файл титров с диска в память'
                    f'\n*buffer_title: {buffer_title}'
                    )
            print(msg)
            self.logger.error(msg) 
            return None 
            
        # Выбирает и подготавливает словарь стоп-слов с учетом языка файла титров
        swords = self.filtering.training_vocab(buffer_title, replace_dict)
        if not swords:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не создали словарь стоп-слов: {swords}'
                    ) 
            print(msg)
            self.logger.error(msg)
            return None
        
        # Заменяет стоп-слова в буфере согласно словарю
        new_buf = self.replace_swords_buffer(buffer_title, swords, punctuation)
        if not new_buf:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не создали новый буфер файла титров {new_buf}'
                ) 
            print(msg)
            self.logger.error(msg)
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



# MAIN **************************
def main():
    # Создаем экземпляр класса Start
    start = Start()
    name_method = start.get_current_method_name()

    msg = (f'\n[{start.cls_name}|{name_method}]'
           f'\nStart...') 
    print(msg)

    full_path_title = start.srt_file
    replace_dictionary = start.replace_dict
    punctuation = start.punct
    new_name_title = start.new_name_title
    config_path = start.config_path

    # удаляем старые логги
    print(f'Всего удалили [{start.cleaning.delete_logs(config_path, 1000)}] старых файлов журналов логгов')

    # выполняем основной скрипт
    full_path_saving_title = start.process_title(full_path_title, 
                                                replace_dictionary, 
                                                punctuation, 
                                                new_name_title)
    if not full_path_saving_title:
        msg = (
                f'\n*ERROR [{name_method}|{start.cls_name}]'
                f'\n*Не создали новый файл титров'
                f'\n*full_path_saving_title {full_path_saving_title}'
                ) 
        print(msg)
        start.logger.error(msg)

    msg = (
            f'\n# [{name_method}|{start.cls_name}]'
            f'\n# Cоздали новый файл титров'
            f'\n# full_path_saving_title {full_path_saving_title}'
            ) 
    print(msg)

    # Пауза в конце выполнения скрипта перед закрытием окна
    input("\nНажмите клавишу <Enter> для выхода...")


if __name__ == "__main__":
    main()



