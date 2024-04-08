

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



class Cleaning(ConfigInitializer):
    """
    Module for class for defining methods for working with the operating system, 
    files, etc.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Cleaning.countInstance += 1
        self.countInstance = Cleaning.countInstance

        self.abspath = dirname(abspath(__file__))
        self.cls_name = self.__class__.__name__
        self.config_path = join(dirname(abspath(__file__)), 'config.json')
        # Logger
        self.log_init = LogInitializer()
        self.logger = self.log_init.initialize(self.config_path)
        # Prints
        self.prints = Prints()
        self.prints.print_class()


    # удаляем файлы из директорий старше определенного срока
    def delete_old_files(self, directories: List[str], time_delete: int) -> List[str]:
        """
        Метод для удаления файлов и папок из указанных директорий, 
        которые старше определенного срока.

        Аргументы:
            directories (List[str]): Список строк, представляющих пути к директориям, 
            из которых нужно удалить файлы и папки.
            time_delete (int): Время в секундах, определяющее, 
            насколько старые должны быть файлы и папки, чтобы быть удаленными.

        Возвращаемое значение:
            List[str]: Список строк, представляющих пути к удаленным файлам и папкам.

        :return: Список строк с путями к удаленным файлам и папкам.
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def  _delete_old_files():
            
            deleted_files_and_dirs = []  # список для хранения путей к удаленным файлам и папкам
            
            for directory in directories:
                # множество имен файлов и папок, которые находятся на диске
                set_nfile_dir = set(listdir(directory))
                # текущее время
                current_time = dt.now().timestamp()
                
                for name_file in set_nfile_dir:
                    
                    full_path = join(directory, name_file)
                    
                    # время последнего изменения файла или папки
                    file_mod_time = getmtime(full_path)
                    
                    # если файл или папка старше time_delete
                    if current_time - file_mod_time > time_delete:
                        if isdir(full_path):
                            shutil.rmtree(full_path)
                            deleted_files_and_dirs.append(full_path)
                            print(f"\n[{__name__}|{self.cls_name}] Директория {full_path} успешно удалена.")
                            self.logger.log_info(f"[{__name__}|{self.cls_name}] Директория {full_path} успешно удалена.")
                        else:
                            remove(full_path)
                            deleted_files_and_dirs.append(full_path)
                            print(f"\n[{__name__}|{self.cls_name}] Файл {full_path} успешно удалён.") 
                            self.logger.log_info(f"[{__name__}|{self.cls_name}] Файл {full_path} успешно удалён.") 
            
            return deleted_files_and_dirs
        return _delete_old_files()



