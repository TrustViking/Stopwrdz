

import chardet
from io import BytesIO
from os.path import split, splitext, join,  exists 
from typing import List, Union
#
from app_env.base_class import BaseClass
from app_env.decorators import safe_execute

class Saving(BaseClass):
    """
    Класс `Saving` предназначен для сохранения содержимого буфера на диск 
        в зависимости от его типа, 
        определения уникального пути к файлу 
        и определения кодировки буфера.

    Attributes:
        countInstance (int): Статический атрибут для подсчета количества экземпляров класса.
    """

    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Saving.countInstance += 1
        self.countInstance = Saving.countInstance

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__


    def get_unique_file_path(self, file_path: str) -> str:
        """
        Получает уникальный путь к файлу, добавляя к имени файла цифру, 
        если файл с таким именем уже существует.

        Args:
            file_path (str): Полный путь к файлу.

        Returns:
            str: Уникальный полный путь к файлу.
        """
        # имя метода            
        name_method = self.get_current_method_name()

        @safe_execute(logger=self.logger, name_method=f'[{self.cls_name}|{name_method}]')
        def  _get_unique_file_path():
            
            # Разделение пути на директорию и имя файла
            directory, filename = split(file_path)

            # Разделение имени файла на основное имя и расширение 
            # (base_name: swords_title, extension: .srt)
            base_name, extension = splitext(filename)
            
            # Переменная для хранения уникального имени файла
            unique_file_name = filename
            # Счетчик для добавления цифры к имени файла
            counter = 2

            # Проверка существования файла по заданному пути
            while exists(join(directory, unique_file_name)):
                # Формирование нового имени файла с добавлением цифры к основному имени
                unique_file_name = f"{base_name}_{counter}{extension}"
                counter += 1

            # Формирование полного пути к уникальному файлу
            unique_file_path = join(directory, unique_file_name)

            return unique_file_path
        return _get_unique_file_path()
    

    # определяем кодировку буффера 
    def encoding_buffer(self,  buffer: Union[BytesIO, list, str, bytes]) -> Union[str, None]:
        """
        Определяет кодировку буфера с помощью библиотеки chardet.

        Args:
            buffer (Union[BytesIO, list, str, bytes]): Буфер для определения кодировки.
                Может быть объектом BytesIO, списком строк, строкой символов или строкой байтов.

        Returns:
            Union[str, None]: Кодировка буфера, если удалось определить, None в противном случае.
        """                
        # имя метода            
        name_method = self.get_current_method_name()

        # Определяем тип буфера и приводим его к форме bytes
        if isinstance(buffer, str):
            byte_buffer = buffer.encode()
        elif isinstance(buffer, list):
            byte_buffer = '\n'.join(buffer).encode()
        elif isinstance(buffer, BytesIO):
            buffer.seek(0)
            byte_buffer = buffer.read()
            buffer.seek(0)
        elif isinstance(buffer, bytes):
            byte_buffer = buffer
        else:
            msg = (f'\n*ERROR [{self.cls_name}|{name_method}]'
                   f'\n*ERROR: Invalid buffer type: [{type(buffer)}]')
            print(msg)
            self.logger.error(msg)
            raise TypeError(f'Invalid buffer type: [{type(buffer)}]')

        try:
            # Определение кодировки с помощью chardet
            result = chardet.detect(byte_buffer)
            return result['encoding']

        except (UnicodeDecodeError, UnicodeEncodeError, LookupError, AttributeError) as eR:
            msg = (f'\n*ERROR [{self.cls_name}|{name_method}]'
                   f'\n*ERROR: {eR}')
            print(msg)
            self.logger.error(msg)
            return None


    # записывает четыре типа буфера на диск (str | List[str] | BytesIO | bytes)
    def save_buffer_disk(self, 
                         file_path: str, 
                         buffer: Union[str, List[str], BytesIO, bytes]
                         ) -> Union[str, None]:
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

        # имя метода            
        name_method = self.get_current_method_name()

               
        if isinstance(buffer, str):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(buffer)
            except (FileNotFoundError, PermissionError, OSError) as eR:
                msg = (
                        f'\n*ERROR [{self.cls_name}|{name_method}]'
                        f'\n*ERROR: {eR}'
                        )
                print(msg)
                self.logger.error(msg)
                return None  
        
        elif isinstance(buffer, list):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(buffer))
            except (FileNotFoundError, PermissionError, OSError) as eR:
                msg = (
                        f'\n*ERROR [{self.cls_name}|{name_method}]'
                        f'\n*ERROR: {eR}'
                        )
                print(msg)
                self.logger.error(msg)
                return None  
        
        elif isinstance(buffer, BytesIO):
            try:
                buffer.seek(0)
                with open(file_path, 'wb') as f:
                    f.write(buffer.getvalue())
            except (FileNotFoundError, PermissionError, OSError) as eR:
                msg = (
                        f'\n*ERROR [{self.cls_name}|{name_method}]'
                        f'\n*ERROR: {eR}'
                        )
                print(msg)
                self.logger.error(msg)
                return None  
        
        elif isinstance(buffer, bytes):
            try:
                with open(file_path, 'wb') as f:
                    f.write(buffer)
            except (FileNotFoundError, PermissionError, OSError) as eR:
                msg = (
                        f'\n*ERROR [{self.cls_name}|{name_method}]'
                        f'\n*ERROR: {eR}'
                        )
                print(msg)
                self.logger.error(msg)
                return None                
        
        else:
            print(f'\n*ERROR[{self.cls_name}|{name_method}] Invalid buffer type: {type(buffer)}') 
            self.logger.error(f'\n*ERROR[{self.cls_name}|{name_method}] Invalid buffer type: {type(buffer)}') 
            return None  # Возвращаем None, если передан неподдерживаемый тип буфера

        return file_path # Возвращаем полный путь файла, если запись прошла успешно
            


