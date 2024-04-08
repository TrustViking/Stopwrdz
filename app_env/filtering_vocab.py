




import shutil
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex 
from pynvml import nvmlDeviceGetMemoryInfo, nvmlShutdown
from psutil import virtual_memory
from logging import getLevelName
from time import strftime
from os.path import basename, join, abspath, dirname, getmtime, isdir, isfile, exists
from os import makedirs, listdir, remove
from sys import platform, argv, path
from typing import Coroutine, List, Optional, Dict, Union
from time import sleep, strftime
from datetime import datetime as dt
import chardet
from io import BytesIO
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from json import load, JSONDecodeError
#
from app_env.decorators import safe_execute
from app_env.app_init import LogInitializer, ConfigInitializer
from app_env.systems_methods import SysMethods
from app_env.prints_screen import Prints
from app_env.saving import Saving
from app_env.reading import Reading

class Filtering(ConfigInitializer):
    """
    Class that determines the encoding of the stop words file, 
    loads the stop words file into memory, 
    removes duplicate words from the file, 
    sorts the words in the file and writes the file to disk.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Filtering.countInstance += 1
        self.countInstance = Filtering.countInstance

        self.abspath = dirname(abspath(__file__))
        self.cls_name = self.__class__.__name__
        # config
        self.config_path = join(dirname(abspath(__file__)), 'config.json')
        self.config = self.read_config(self.config_path)
        # Logger
        self.log_init = LogInitializer()
        self.logger = self.log_init.initialize(self.config_path)
        # Reading
        self.reading = Reading()
        # Saving
        self.saving = Saving()
        # SysMethods
        self.sysmethods = SysMethods()
        # Prints
        self.prints = Prints()
        self.prints.print_class()



    def filtering_vocab(self, file_path: str):
        """
        Определяем кодировку файла словаря стоп-слов, 
        загружает файл стоп-слов в память, 
        убирает повторы слов в файле, 
        сортирует слова в файле,
        записывает файл на диск

        :param file_path: полный путь к файлу стоп-слов
        :return: полный путь к перезаписанному файлу
        """
        
        if not exists(file_path) or not isfile(file_path):
            msg = (
                    f'\n*ERROR [{__name__}|{self.cls_name}] ERROR'
                    f'\n*Проверьте полный путь к файлу стоп-слов: {file_path}' 
                    )
            print(msg)
            return None
        
        # определяем кодировку файла стоп-слов
        encoding = self.reading.encoding_file(file_path)
        if not encoding:
            msg = (
                    f'\n*ERROR [{__name__}|{self.cls_name}]'
                    f'\n*Не определили кодировку после фильтрации файла стоп-слов'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            return None
        

        # чтение файла с диска в память построчно (т.е. список слов)
        stop_words = self.reading.read_file_to_buffer_lines(file_path, encoding)
        if not stop_words:
            msg = (
                    f'\n*ERROR [{__name__}|{self.cls_name}]'
                    f'\n*Не загрузили файл стоп-слов в память'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            return None

        # Добавление вариантов слов с большой и маленькой буквы,
        # а также как есть (особенно для названий: YouTube...)
        case_sensitive_words = set()
        for word in set(filter(lambda x: x.strip(), stop_words)):
             # Проверка, состоит ли "слово" из нескольких слов
            if ' ' in word:
                continue  # Пропустить, если "слово" на самом деле фраза
            case_sensitive_words.add(word)
            case_sensitive_words.add(word.lower())
            case_sensitive_words.add(word.capitalize())            

        # Сортировка vocab
        vocab = sorted(case_sensitive_words)

        # запись vocab в файл на диск
        result_saving = self.saving.save_buffer_lines_to_disk(file_path, encoding, vocab)
        if result_saving is None:
            msg = (
                    f'\n*ERROR [{__name__}|{self.cls_name}]'
                    f'\n*Не записали файл стоп-слов на диск'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            return None
        elif result_saving:
            msg = (
                    f'\n[{__name__}|{self.cls_name}]'
                    f'\nФайл {basename(file_path)}' 
                    f'\nПуть к файлу: {dirname(file_path)}'
                    f'\nФайл успешно записан'
                    )
            print(msg)
        else:
            msg = (
                    f'\n*ERROR [{__name__}|{self.cls_name}]'
                    f'\n*Ошибка при записи файла'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
        
        return file_path



    # определяем язык буффера
    # возвращаем строку 'en', 'ru', 'ro' or None
    def detection_lang(self, buffer: List[str]) -> Union[str, None]:
        """
        Определяет язык текста в буфере с помощью библиотеки langdetect.

        Args:
            buffer (List[str]): Список строк текста.

        Returns:
            Union[str, None]: Код языка текста (например, 'en', 'ru', 'ro') 
            или None, если язык не удалось определить.
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _detection_lang():
            
            # DEBUG определяем кодировку буффера 
            encoding=self.saving.encoding_buffer(buffer)
            # Выводим сообщение о текущей кодировке буфера
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nБуфер в кодировке: {encoding}'
                    )
            print(msg)
            
            # # Декодируем буфер в текст, используя определенную кодировку
            # text = [line.decode(encoding=encoding) for line in buffer.readlines()]
            
            try:
                # Определяем и возвращаем язык текста с помощью библиотеки langdetect
                return detect(' '.join(buffer))
            
            except LangDetectException as eR:
                print(f'\n*ERROR [{__name__}|{self.cls_name}] LangDetectException: {eR}')
                self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] LangDetectException: {eR}') 
                return None
            except UnicodeDecodeError as eU:
                print(f'\n*ERROR [{__name__}|{self.cls_name}] UnicodeDecodeError: {eU}')
                self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] UnicodeDecodeError: {eU}') 
                return None
        return _detection_lang()


    def diction_swords(self, file_path: str, replace_dict: Dict[str, str]) -> Union[Dict[str, str], None]:
        """
        Загружает слова из файла и создает словарь стоп-слов и их замен.

        Args:
            file_path (str): Полный путь к файлу словаря стоп-слов
            replace_dict (Dict[str, str]): Словарь для замены символов.

        Returns:
            Union[Dict[str, str], None]: Словарь, 
            где ключ - исходное слово, 
            значение - измененное слово.
            None, если произошла ошибка при чтении файла или определении кодировки.
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _diction_swords():
            
            word_dict = {}

            # Проверяем, существует ли файл по указанному пути и является ли он файлом
            if not exists(file_path) or not isfile(file_path):
                msg = (
                        f'\n*ERROR [{__name__}|{self.cls_name}] ERROR'
                        f'\n*Проверьте полный путь к файлу стоп-слов: {file_path}' 
                        )
                print(msg)
                return None


            # определяем кодировку файла стоп-слов
            encoding = self.reading.encoding_file(file_path)
            if not encoding:
                msg = (
                        f'\n*ERROR [{__name__}|{self.cls_name}]'
                        f'\n*Не определили кодировку после фильтрации файла стоп-слов'
                        f'\n*Файл {basename(file_path)}' 
                        f'\n*Путь к файлу: {dirname(file_path)}'
                        )
                print(msg)
                return None

            try:
                # Читаем файл и создаем словарь стоп-слов и их замен
                with open(file_path, 'r', encoding=encoding) as f:
                    for line in f:
                        # Убираем пробелы и переносы строк с обоих концов строки
                        word = line.strip()
                        
                        # Производим замену символов
                        replaced_word = "".join([replace_dict.get(char, char) for char in word])
                        
                        # Сохраняем в словаре
                        word_dict[word] = replaced_word
            
            except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as eR:
                    print(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None
            # debug
            first_five_values = list(word_dict.values())[:5]
            msg = (
                    f'\nDEBUG [{__name__}|{self.cls_name}]'
                    f'\nFirst_five_values word_dict: {first_five_values}'
                    )
            print(msg)
            
            return word_dict
        return _diction_swords()


    def training_vocab(self, 
                       buffer_title: List[str],  # Буфер с текстом титров в виде списка строк UTF-8
                       path_pattern_vocab: str,  # Шаблон пути к словарю по языкам
                       replace_dict: Dict[str, str],  # Словарь для замены символов  
                        )-> Optional[Dict[str, str]]:
        """
        Выбирает и подготавливает словарь стоп-слов 
        с учетом языка файла титров.

        Args:
            self: Экземпляр класса.
            buffer_title (BytesIO): Буфер с данными титров в формате BytesIO.
            path_pattern_vocab (str): Шаблон пути к словарю по языкам.
            replace_dict (Dict[str, str]): Словарь для замены символов.

        Returns:
            Optional[Dict[str, str]]: Словарь стоп-слов и их замен.
            Если произошла ошибка, возвращает None.
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _training_vocab():

            # определяем язык буфера титров для выбора языка словаря стоп-слов
            language = self.detection_lang(buffer_title)
            if not language:
                msg = (
                        f'\n*ERROR [{__name__}|{self.cls_name}]'
                        f'\n*Не определили язык титров language: {language}'
                        )
                print(msg)
                self.logger.log_info(msg) 
                return None
            print(f'\n[{__name__}|{self.cls_name}] language: {language}')
            
            # формируем путь к словарю исходя из определенного языка титров
            path_vocab = path_pattern_vocab+language.upper()+'.txt'
            print(f'\n[{__name__}|{self.cls_name}] path_vocab: {path_vocab}')

            # подготавливаем (фильтруем) файл словарь стоп-слов 
            # (убираем повторы, сортируем и перезаписываем)
            # full_path_swords = self.filtering.filtering_vocab(path_vocab)
            full_path_vocab = self.filtering_vocab(path_vocab)
            if not full_path_vocab:
                msg = (f'\n*ERROR [{__name__}|{self.cls_name}]' 
                    f'\n*Не отфильтровали файл стоп-слов full_path_swords: {full_path_vocab}'
                        )
                print(msg)
                self.logger.log_info(msg) 
                return None
            
            # создаем словарь стоп-слов и их замен
            swords = self.diction_swords(full_path_vocab, replace_dict)
            if not swords:
                msg = (f'\n*ERROR [{__name__}|{self.cls_name}]'
                    f'\n*Не создали словарь стоп-слов: {swords}'
                    f'\nЯзык: [{language}]') 
                print(msg)
                self.logger.log_info(msg)
                return None
            return swords
        return _training_vocab()





