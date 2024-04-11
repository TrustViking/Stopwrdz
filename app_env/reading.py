

import chardet
from os.path import basename, dirname
from typing import List, Optional

from app_env.base_class import BaseClass
from app_env.saving import Saving

class Reading(BaseClass):
    """
    Класс `Reading` предназначен для чтения файлов с диска, определения их кодировки и хранения содержимого в буфере памяти.

    Attributes:
        countInstance (int): Статический атрибут для подсчета количества экземпляров класса.
    """    
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Reading.countInstance += 1
        self.countInstance = Reading.countInstance

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__

        # Saving
        self.saving = Saving()


    # Метод определения кодировки файла
    def encoding_file(self, file_path: str) -> Optional[str]:
        """
        Определяет кодировку файла  с помощью библиотеки chardet

        Args:
            self: Экземпляр класса.
            file_path (str): Путь к файлу

        Returns:
            Optional[str]: Кодировка файла, если определена,
            None в противном случае.
        """       
        
        name_method = self.get_current_method_name()
        
        try:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as eR:
            print(f'\n*ERROR [{self.cls_name}|{name_method}] ERROR: {eR}') 
            self.logger.error(f'\n*ERROR [{self.cls_name}|{name_method}] ERROR: {eR}') 
            return None

        if not result:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}] Не определили кодировку файла'
                    f'\n*Файл {basename(file_path)}' 
                    f'\n*Путь к файлу: {dirname(file_path)}'
                    )
            print(msg)
            self.logger.error(msg)
            return None
        
        msg = (
                f'\n[{self.cls_name}|{name_method}] '
                f'\nПуть к файлу: [{dirname(file_path)}]'
                f'\nФайл: [{basename(file_path)}]' 
                f'\nКодировка: [{result["encoding"]}]'
                )
        print(msg)

        return result['encoding']
    
        
    # Метод чтение файла с диска в буфер памяти в виде списка строк символов
    def read_file_to_buffer_lines(self, file_path: str, encoding: str) -> Optional[List[str]]:
        """
        Читает файл с любой кодировкой с диска в буфер памяти 
        в виде списка строк символов, 
        переводит текст в буфере в кодировку UTF-8

        Args:
            self: Экземпляр класса.
            file_path (str): Путь к файлу.
            encoding (str): Кодировка файла.

        Returns:
            Optional[List[str]]: Содержимое файла в виде списка строк в кодировке UTF-8, 
            если чтение прошло успешно, None в противном случае.
        """        
        name_method = self.get_current_method_name()

        try:
            # Чтение файла в память
            with open(file_path, 'r', encoding=encoding) as f:
                buffer = f.read().splitlines()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as eR:
            print(f'\n*ERROR[{self.cls_name}|{name_method}] ERROR: {eR}') 
            self.logger.error(f'\n*ERROR[{self.cls_name}|{name_method}] ERROR: {eR}') 
            return None
        
        encoding_buffer = self.saving.encoding_buffer(buffer)
        msg = (f'\n[{self.cls_name}|{name_method}]'
                f'\nБуфер в кодировке: [{encoding_buffer}]'
                f'\nТип буфера: [{type(buffer)}]'
                )
        print(msg)

        # Преобразование каждой строки в кодировке файла в UTF-8
        buffer_utf8 = [line.encode(encoding_buffer).decode() for line in buffer]
        
        return buffer_utf8





