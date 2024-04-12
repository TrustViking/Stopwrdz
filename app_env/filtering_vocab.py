

from os.path import basename, dirname, isfile, exists
from typing import List, Optional, Dict, Union
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from app_env.saving import Saving
from app_env.reading import Reading
from app_env.base_class import BaseClass


class Filtering(BaseClass):
    """
    Класс, определяющий кодировку файла стоп-слов, 
    загружает файл стоп-слов в память, 
    удаляет из файла дублирующиеся слова, 
    сортирует слова в файле и записывает файл на диск.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Filtering.countInstance += 1
        self.countInstance = Filtering.countInstance

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__

        # Reading
        self.reading = Reading()
        # Saving
        self.saving = Saving()


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
        name_method = self.get_current_method_name()

        if not exists(file_path) or not isfile(file_path):
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}] ERROR'
                    f'\n*Проверьте полный путь к файлу стоп-слов: {file_path}' 
                    )
            print(msg)
            self.logger.error(msg)
            return None
        
        # определяем кодировку файла стоп-слов
        encoding = self.reading.encoding_file(file_path)
        if not encoding:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не определили кодировку после фильтрации файла стоп-слов'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            self.logger.error(msg)
            return None
        

        # чтение файла с диска в память построчно (т.е. список стоп-слов)
        stop_words = self.reading.read_file_to_buffer_lines(file_path, encoding)
        if not stop_words:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не загрузили файл стоп-слов в память'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            self.logger.error(msg)
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
        result_saving = self.saving.save_buffer_disk(file_path, vocab)
        if result_saving is None:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не записали файл стоп-слов на диск'
                    f'\n*Файл: {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            self.logger.error(msg)
            return None
        
        elif result_saving:
            msg = (
                    f'\n[{self.cls_name}|{name_method}]'
                    f'\nФайл словаря подготовлен и перезаписан'
                    f'\nФайл: [{basename(file_path)}]'
                    f'\nПуть к файлу: [{dirname(file_path)}]'
                    )
            print(msg)
        
        else:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Ошибка при перезаписи подготовленного файла словаря'
                    f'\n*Файл: {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            self.logger.error(msg)
        
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
        name_method = self.get_current_method_name()
       
        try:
            # Определяем и возвращаем язык текста с помощью библиотеки langdetect
            return detect(' '.join(buffer))
        
        except LangDetectException as eR:
            print(f'\n*ERROR [{self.cls_name}|{name_method}] LangDetectException: {eR}')
            self.logger.error(f'\n*ERROR [{self.cls_name}|{name_method}] LangDetectException: {eR}') 
            return None
        except UnicodeDecodeError as eU:
            print(f'\n*ERROR [{self.cls_name}|{name_method}] UnicodeDecodeError: {eU}')
            self.logger.error(f'\n*ERROR [{self.cls_name}|{name_method}] UnicodeDecodeError: {eU}') 
            return None


    def diction_swords(self, 
                       file_path: str, 
                       replace_dictionary: Dict[str, str]
                       ) -> Union[Dict[str, str], None]:
        """
        Загружает слова из файла и создает словарь стоп-слов и их замен.

        Args:
            file_path (str): Полный путь к файлу словаря стоп-слов
            replace_dictionary (Dict[str, str]): Словарь для замены символов.

        Returns:
            Union[Dict[str, str], None]: Словарь, 
            где ключ - исходное слово, 
            значение - измененное слово.
            None, если произошла ошибка при чтении файла или определении кодировки.
        """        
        name_method = self.get_current_method_name()

        # словарь замен стоп-слов на зашифрованные стоп-слова
        word_diction = {}
        # Проверяем, существует ли файл по указанному пути и является ли он файлом
        if not exists(file_path) or not isfile(file_path):
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}] ERROR'
                    f'\n*Проверьте полный путь к файлу стоп-слов: {file_path}' 
                    )
            print(msg)
            self.logger.error(msg)
            return None

        # определяем кодировку файла стоп-слов
        encoding = self.reading.encoding_file(file_path)
        if not encoding:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не определили кодировку после фильтрации файла стоп-слов'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            self.logger.error(msg)
            return None
        
        msg = (
                f'\n[{self.cls_name}|{name_method}]'
                f'\nЗначения из словаря замены букв (replace_dictionary):'
                )
        print(msg)
        for key, value in replace_dictionary.items():
            print(f"Ключ: {key}, Значение: {value}")

        try:
            # Читаем файл и создаем словарь стоп-слов и их замен
            with open(file_path, 'r', encoding=encoding) as f:
                for line in f:
                    # Убираем пробелы и переносы строк с обоих концов строки
                    word = line.strip()
                    
                    # Производим замену символов
                    replaced_word = "".join([replace_dictionary.get(char, char) for char in word])
                    
                    # Сохраняем в словаре
                    word_diction[word] = replaced_word
        
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as eR:
                print(f'\n*ERROR [{self.cls_name}|{name_method}] ERROR: {eR}') 
                self.logger.error(f'\n*ERROR [{self.cls_name}|{name_method}] ERROR: {eR}') 
                return None
        
        return word_diction


    def training_vocab(self, 
                       buffer_title: List[str],  # Буфер в кодировке UTF-8 в виде списка строк
                       path_pattern_vocab: str,  # Шаблон пути к словарю по языкам
                       replace_dictionary: Dict[str, str],  # Словарь для замены символов  
                        )-> Optional[Dict[str, str]]:
        """
        Выбирает и подготавливает словарь стоп-слов 
        с учетом языка файла титров.

        Args:
            self: Экземпляр класса.
            buffer_title (BytesIO): Буфер с данными титров в формате BytesIO.
            path_pattern_vocab (str): Шаблон пути к словарю по языкам.
            replace_dictionary (Dict[str, str]): Словарь для замены символов.

        Returns:
            Optional[Dict[str, str]]: Словарь стоп-слов и их замен.
            Если произошла ошибка, возвращает None.
        """        
        name_method = self.get_current_method_name()
        
        # определяем язык буфера титров для выбора языка словаря стоп-слов
        language = self.detection_lang(buffer_title)
        if not language:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Не определили язык титров language: [{language}]'
                    )
            print(msg)
            self.logger.error(msg) 
            return None
        
        msg = (
                f'\n[{self.cls_name}|{name_method}]'
                f'\nlanguage: [{language}]'
                )
        print(msg)
        
        # формируем путь к словарю исходя из определенного языка титров
        path_vocab = path_pattern_vocab+language.upper()+'.txt'
        msg = (
                f'\n[{self.cls_name}|{name_method}]'
                f'\npath_vocab: [{path_vocab}]'
                )
        print(msg)

        # подготавливаем (фильтруем) файл словарь стоп-слов 
        # (убираем повторы, сортируем и перезаписываем)
        full_path_vocab = self.filtering_vocab(path_vocab)
        if not full_path_vocab:
            msg = (f'\n*ERROR [{self.cls_name}|{name_method}]' 
                f'\n*Не отфильтровали файл стоп-слов full_path_swords: {full_path_vocab}'
                    )
            print(msg)
            self.logger.error(msg) 
            return None
        
        # создаем словарь стоп-слов и их замен
        swords = self.diction_swords(full_path_vocab, replace_dictionary)
        if not swords:
            msg = (f'\n*ERROR [{self.cls_name}|{name_method}]'
                f'\n*Не создали словарь стоп-слов: {swords}'
                f'\nЯзык: [{language}]') 
            print(msg)
            self.logger.error(msg)
            return None
        return swords





