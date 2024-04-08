

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



class SysMemory(ConfigInitializer):
    """
    Module for class for defining methods for working with the operating system, 
    files, memory, etc.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        SysMemory.countInstance += 1
        self.countInstance = SysMemory.countInstance

        self.abspath = dirname(abspath(__file__))
        self.cls_name = self.__class__.__name__
        self.config_path = join(dirname(abspath(__file__)), 'config.json')
        # Logger
        self.log_init = LogInitializer()
        self.logger = self.log_init.initialize(self.config_path)
        # Prints
        self.prints = Prints()
        self.prints.print_class()


    # выводим состояние системы
    def system_status(self) -> None:
        """
        Метод для логирования информации о памяти, 
        включая использование оперативной памяти (RAM)
        и памяти графических процессоров (GPU).

        Этот метод использует библиотеку NVML для сбора информации о памяти GPU

        :return: None
        """
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _system_status():
            file_start = basename(argv[0]) #  [start_hasher.py]
            print(f'\n[{__name__}|{self.cls_name}] Start...\n')  
            # Получение абсолютного пути к текущему исполняемому файлу
            file_path = abspath(__file__) #  [D:\linux\bots\bot_hasher\start_hasher.py]
            # Получение пути к директории, в которой находится текущий файл
            current_directory = dirname(file_path)
            msg = (
                    f'File: [{file_start}]\n'
                    f'Current_directory: [{current_directory}]\n'
                    f'Path file: [{file_path}]\n'
                    f'Data memory:'
                    )
            print(msg)
            memory = virtual_memory()
            for field in memory._fields:
                print(f"{field}: {getattr(memory, field)}")    
        return _system_status()


    # Метод для логирования информации о памяти
    def log_memory(self)-> None:
        """
        Метод для логирования информации о памяти, 
        включая использование оперативной памяти (RAM) 
        и памяти графических процессоров (GPU).
        
        Метод логирует информацию о использовании оперативной памяти 
        и памяти каждого графического процессора в логгер с уровнем, 
        установленным в конфигурационном файле

        :return: None
        """        
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _log_memory():
            self.logger.log_info(f'****************************************************************')
            self.logger.log_info(f'*Data RAM {basename(argv[0])}: [{virtual_memory()[2]}%]')
            # Инициализируем NVML для сбора информации о GPU
            nvmlInit()
            deviceCount = nvmlDeviceGetCount()
            self.logger.log_info(f'\ndeviceCount [{deviceCount}]')
            for i in range(deviceCount):
                handle = nvmlDeviceGetHandleByIndex(i)
                meminfo = nvmlDeviceGetMemoryInfo(handle)
                self.logger.log_info(f"#GPU [{i}]: used memory [{int(meminfo.used / meminfo.total * 100)}%]")
                self.logger.log_info(f'****************************************************************\n')
            # Освобождаем ресурсы NVML
            nvmlShutdown()
        return _log_memory()


