

import chardet
import shutil
from io import BytesIO
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex 
from pynvml import nvmlDeviceGetMemoryInfo, nvmlShutdown
from psutil import virtual_memory
from os.path import basename, join, abspath, dirname, getmtime, isdir, isfile
from os import makedirs, listdir, remove
from sys import platform, argv, path
from typing import Coroutine, List, Optional, Dict, Union
from time import sleep, strftime
from datetime import datetime as dt
from json import load, JSONDecodeError
#
from app_env.decorators import safe_execute
from app_env.app_init import LogInitializer, ConfigInitializer
from app_env.prints_screen import Prints



class Reading(ConfigInitializer):
    """
    Module for class for defining methods for working with the operating system, 
    files, etc.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Reading.countInstance += 1
        self.countInstance = Reading.countInstance

        self.abspath = dirname(abspath(__file__))
        self.cls_name = self.__class__.__name__
        self.config_path = join(dirname(abspath(__file__)), 'config.json')
        # Logger
        self.log_init = LogInitializer()
        self.logger = self.log_init.initialize(self.config_path)
        # Prints
        self.prints = Prints()
        self.prints.print_class()



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
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _encoding_file():
            try:
                with open(file_path, 'rb') as f:
                    result = chardet.detect(f.read())
            except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as eR:
                print(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                return None

            if not result:
                msg = (
                        f'\n[{__name__}|{self.cls_name}] Не определили кодировку файла'
                        f'\nФайл {basename(file_path)}' 
                        f'\nПуть к файлу: {dirname(file_path)}'
                        )
                print(msg)
                return None
            
            msg = (
                    f'\n[{__name__}|{self.cls_name}] '
                    f'\nОбщий результат [{result}]'
                    f'\nКодировка [{result['encoding']}]'
                    f'\nФайл {basename(file_path)}' 
                    f'\nПуть к файлу: {dirname(file_path)}'
                    )
            print(msg)

            return result['encoding']
        return _encoding_file()
    
        
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
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _read_file_to_buffer_lines():
            try:
                # Чтение файла в память
                with open(file_path, 'r', encoding=encoding) as f:
                    buffer = f.read().splitlines()
            except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as eR:
                print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                return None
            
            # Преобразование строк в кодировке файла в UTF-8
            buffer_utf8 = [line.encode('utf-8').decode('utf-8') for line in buffer]
            
            return buffer_utf8
        return _read_file_to_buffer_lines()


    # Метод читает файл с диска в буфер в виде объекта BytesIO
    def read_file_to_buffer_bytes(self, file_path: str) -> Optional[BytesIO]:
            """
            Читает файл с диска в буфер в виде объекта BytesIO

            Args:
                self: Экземпляр класса.
                file_path (str): Путь к файлу.

            Returns:
                Optional[io.BytesIO]: Объект BytesIO, содержащий содержимое файла,
                если чтение прошло успешно, None в противном случае.
            """
            @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
            def _read_file_to_buffer_bytes():
                try:
                    # Создаем объект BytesIO
                    buffer = BytesIO()
                    # Чтение файла и запись его содержимого в буфер
                    with open(file_path, 'rb') as f:
                        buffer.write(f.read())
                    # Устанавливаем позицию указателя буфера в начало
                    buffer.seek(0)
                except (FileNotFoundError, PermissionError, OSError) as eR:
                    print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None

                return buffer
            return _read_file_to_buffer_bytes()



