

import chardet
import shutil
from io import BytesIO
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex 
from pynvml import nvmlDeviceGetMemoryInfo, nvmlShutdown
from psutil import virtual_memory
from os import makedirs, listdir, remove
from os.path import getmtime, isdir, isfile, split, splitext
from os.path import basename, join, abspath, dirname, exists 
from sys import platform, argv, path
from typing import Coroutine, List, Optional, Dict, Union
from time import sleep, strftime
from datetime import datetime as dt
from json import load, JSONDecodeError
#
from app_env.decorators import safe_execute
from app_env.app_init import LogInitializer, ConfigInitializer
from app_env.prints_screen import Prints



class Saving(ConfigInitializer):
    """
    Module for class for defining methods for working with the operating system, 
    files, etc.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Saving.countInstance += 1
        self.countInstance = Saving.countInstance

        self.abspath = dirname(abspath(__file__))
        self.cls_name = self.__class__.__name__
        self.config_path = join(dirname(abspath(__file__)), 'config.json')
        # Logger
        self.log_init = LogInitializer()
        self.logger = self.log_init.initialize(self.config_path)
        # Prints
        self.prints = Prints()
        self.prints.print_class()



    # Метод для создания директорий, если они не существуют
    def create_directory(self, paths: list[str]) -> None:
        """
        Метод для создания директорий, если они не существуют.

        Аргументы:
            paths (list[str]): Список строк, каждая из которых является путем к директории, 
            которую необходимо создать.

        Возвращаемое значение:
            None. Метод ничего не возвращает, только создает директории.

        :return: None
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def  _create_directory():

            _ = [makedirs(path,  exist_ok=True) for path in paths]

        return _create_directory()


    def get_unique_file_path(self, file_path: str) -> str:
            """
            Получает уникальный путь к файлу, добавляя к имени файла цифру, 
            если файл с таким именем уже существует.

            Args:
                file_path (str): Полный путь к файлу.

            Returns:
                str: Уникальный полный путь к файлу.
            """
            @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
            def  _get_unique_file_path():
                # Разделение пути на директорию и имя файла
                directory, filename = split(file_path)

                # DEBUG  
                msg = (
                        f'\nDEBUG [{__name__}|{self.cls_name}]'
                        f'\nfile_path: {file_path}'
                        f'\ndirectory: {directory}'
                        f'\nfilename: {filename}'
                        )
                print(msg)

                # Разделение имени файла на основное имя и расширение
                base_name, extension = splitext(filename)
                
                # DEBUG  
                msg = (
                        f'\nDEBUG [{__name__}|{self.cls_name}]'
                        f'\nfilename: {filename}'
                        f'\nbase_name: {base_name}'
                        f'\nextension: {extension}'
                        )
                print(msg)
                
                # Переменная для хранения уникального имени файла
                unique_file_name = filename
                # Счетчик для добавления цифры к имени файла
                counter = 2

                # Проверка существования файла по заданному пути
                while exists(join(directory, unique_file_name)):
                    # Формирование нового имени файла с добавлением цифры к основному имени
                    unique_file_name = f"{base_name}_{counter}{extension}"
                    # DEBUG  
                    msg = (
                            f'\nDEBUG [{__name__}|{self.cls_name}]'
                            f'\nfull path: {join(directory, unique_file_name)}'
                            f'\nunique_file_name: {unique_file_name}'
                            )
                    print(msg)
                    counter += 1

                # Формирование полного пути к уникальному файлу
                unique_file_path = join(directory, unique_file_name)

                return unique_file_path
            return _get_unique_file_path()


    # определяем кодировку буффера 
    def encoding_buffer(self, buffer: Union[BytesIO, List[str], str]) -> Union[str, None]:
        """
        Определяет кодировку буфера с помощью библиотеки chardet

        Args:
            self: Экземпляр класса.
            buffer (Union[BytesIO, List[Union[str, bytes]], str]): Буфер для определения кодировки.
                Может быть объектом BytesIO, списком строк, или строкой.

        Returns:
            Union[str, None]: Кодировка буфера, если удалось определить, 
            None в противном случае.
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def  _encoding_buffer():
            
            # Если переданный буфер - строка
            if isinstance(buffer, str):
                try:
                    # Определение кодировки с помощью chardet
                    result = chardet.detect(buffer.encode())
                    print(f'[{__name__}|{self.cls_name}] result: [{result}]')
                    print(f'[{__name__}|{self.cls_name}] result["encoding"]: [{result["encoding"]}]')

                    return result['encoding']

                except (UnicodeDecodeError, UnicodeEncodeError, LookupError, AttributeError) as eR:
                    print(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}')
                    self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}')
                    return None

            # Если переданный буфер - список строк
            elif isinstance(buffer, List[str]):
                # Преобразовываем список строк в одну строку
                buffer_str = '\n'.join(buffer)
                try:
                    # Определение кодировки с помощью chardet
                    result = chardet.detect(buffer_str.encode())
                    print(f'[{__name__}|{self.cls_name}] result: [{result}]')
                    print(f'[{__name__}|{self.cls_name}] result["encoding"]: [{result["encoding"]}]')
                    
                    return result['encoding']
                
                except (UnicodeDecodeError, UnicodeEncodeError, LookupError, AttributeError) as eR:
                    print(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None

            # Если переданный буфер - BytesIO
            elif isinstance(buffer, BytesIO):
                # Получаем текущую позицию указателя файла
                current_position = buffer.tell()
                if current_position>0:
                    buffer.seek(0)
                    current_position=0
                try:
                    # Определение кодировки с помощью chardet
                    result = chardet.detect(buffer.read())
                    print(f'[{__name__}|{self.cls_name}] result: [{result}]')
                    print(f'[{__name__}|{self.cls_name}] result["encoding"]: [{result["encoding"]}]')
                    
                    return result['encoding']
                
                except (UnicodeDecodeError, UnicodeEncodeError, LookupError) as eR:
                    print(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None
                finally:
                    # В любом случае возвращаем указатель файла в начало буфера
                    buffer.seek(current_position)
            

            # Если переданный буфер - список байтов
            elif isinstance(buffer, list) and all(isinstance(item, bytes) for item in buffer):
                # Для списка байтов кодировка, вероятно, не требуется
                msg = (
                        f'\n[{__name__}|{self.cls_name}]'
                        f'\nДля списка байтов кодировка, вероятно, не требуется'
                        f'\nbuffer: {buffer}'
                        )
                print(msg)
                return None
            
            # Если переданный буфер не является ни списком строк, 
            # ни объектом BytesIO, ни списком байтов
            else:
                print(f'\n*ERROR [{__name__}|{self.cls_name}] Invalid buffer type: [{type(buffer)}]') 
                self.logger.log_info(f'\n*ERROR [{__name__}|{self.cls_name}] Invalid buffer type: [{type(buffer)}]') 
                raise TypeError(f'Invalid buffer type: [{type(buffer)}]')

        return _encoding_buffer()


    # Метод записи строк или списков строк на диск (str | List[str])
    def save_buffer_str_disk(self, 
                         file_path: str, 
                         buffer: Union[str, List[str]]) -> Optional[str]:
        """
        Записывает содержимое буфера на диск в виде строки или списка строк (str | List[str])

        Args:
            self: Экземпляр класса.
            file_path (str): Путь к файлу, в который будет записан буфер.
            buffer: (Union[str, List[str]]) Буфер для записи. 
                Может быть строкой или списком строк.

        Returns:
            Optional[str]: Путь к файлу, если запись прошла успешно, None в случае ошибки.
        """            
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _save_buffer_str_disk():
            if isinstance(buffer, str):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(buffer)
                except (FileNotFoundError, PermissionError, OSError) as eR:
                    print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None  
                
            elif isinstance(buffer, List[str]):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(buffer))
                except (FileNotFoundError, PermissionError, OSError) as eR:
                    print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None  
                
            else:
                print(f'\n*ERROR[{__name__}|{self.cls_name}] Invalid buffer type: {type(buffer)}') 
                self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] Invalid buffer type: {type(buffer)}') 
                return None  # Возвращаем None, если передан неподдерживаемый тип буфера

            return file_path # Возвращаем полный путь файла, если запись прошла успешно
        
        return _save_buffer_str_disk()

    # записывает два типа буфера на диск (BytesIO | bytes)
    def save_buffer_bytes_disk(self, 
                               file_path: str, 
                               buffer: Union[BytesIO, bytes]) -> Optional[str]:
        """
        Записывает содержимое буфера формата BytesIO на диск (BytesIO | bytes)

        Args:
            self: Экземпляр класса.
            file_path (str): Путь к файлу, в который будет записан буфер.
            buffer (Union[BytesIO, bytes]): Буфер, содержащий данные для записи в файл.
                Может быть объектом BytesIO или строкой байтов.

        Returns:
            Optional[str]: Полный путь к файлу, если запись прошла успешно, None в случае ошибки.
        """                    
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _save_buffer_bytes_to_disk():
            if isinstance(buffer, BytesIO):
                try:
                    buffer.seek(0)
                    with open(file_path, 'wb') as f:
                        f.write(buffer.getvalue())
                except (FileNotFoundError, PermissionError, OSError) as eR:
                    print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None  
            
            elif isinstance(buffer, bytes):
                try:
                    with open(file_path, 'wb') as f:
                        f.write(buffer)
                except (FileNotFoundError, PermissionError, OSError) as eR:
                    print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                    return None                
            
            else:
                print(f'\n*ERROR[{__name__}|{self.cls_name}] Invalid buffer type: {type(buffer)}') 
                self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] Invalid buffer type: {type(buffer)}') 
                return None  # Возвращаем None, если передан неподдерживаемый тип буфера
            

            return file_path  # Возвращаем полный путь файла, если запись прошла успешно
        return _save_buffer_bytes_to_disk()


    # записывает четыре типа буфера на диск (str | List[str] | BytesIO | bytes)
    def save_buffer_disk(self, 
                         file_path: str, 
                         buffer: Union[str, List[str], BytesIO, bytes]) -> Union[str, None]:
            """
            Записывает содержимое буфера на диск в соответствии с его типом. 
            Может быть строкой, списком строк, объектом BytesIO или строкой байтов.
            (str | List[str] | BytesIO | bytes)

            Args:
                self: Экземпляр класса.
                file_path (str): Путь к файлу, в который будет записан буфер.
                buffer: (Union[str, List[str], BytesIO, bytes]) Буфер для записи. 
                    Может быть строкой, списком строк, 
                    объектом BytesIO или строкой байтов.

            Returns:
                Union[str, None]: Путь к файлу, если запись прошла успешно, None в случае ошибки.
            """            
            @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
            def _save_buffer_disk():
                if isinstance(buffer, str):
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(buffer)
                    except (FileNotFoundError, PermissionError, OSError) as eR:
                        print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        return None  
                
                elif isinstance(buffer, List[str]):
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(buffer))
                    except (FileNotFoundError, PermissionError, OSError) as eR:
                        print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        return None  
                
                elif isinstance(buffer, BytesIO):
                    try:
                        buffer.seek(0)
                        with open(file_path, 'wb') as f:
                            f.write(buffer.getvalue())
                    except (FileNotFoundError, PermissionError, OSError) as eR:
                        print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        return None  
                
                elif isinstance(buffer, bytes):
                    try:
                        with open(file_path, 'wb') as f:
                            f.write(buffer)
                    except (FileNotFoundError, PermissionError, OSError) as eR:
                        print(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] ERROR: {eR}') 
                        return None                
                
                else:
                    print(f'\n*ERROR[{__name__}|{self.cls_name}] Invalid buffer type: {type(buffer)}') 
                    self.logger.log_info(f'\n*ERROR[{__name__}|{self.cls_name}] Invalid buffer type: {type(buffer)}') 
                    return None  # Возвращаем None, если передан неподдерживаемый тип буфера

                return file_path # Возвращаем полный путь файла, если запись прошла успешно
            
            return _save_buffer_disk()


