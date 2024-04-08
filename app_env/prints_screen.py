


import shutil
from os.path import basename, join, abspath, dirname, getmtime, isdir, isfile
from os import makedirs, listdir, remove
from sys import platform, argv, path
from typing import Coroutine, List, Optional, Dict, Union
from time import sleep, strftime
from datetime import datetime as dt
from json import load, JSONDecodeError
#
from app_env.app_init import LogInitializer, ConfigInitializer
from app_env.decorators import safe_execute


class Prints(ConfigInitializer):
    """
    Class for displaying class attributes and other debugging information on the screen, etc.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Prints.countInstance += 1
        self.countInstance = Prints.countInstance

        self.abspath = dirname(abspath(__file__))
        self.cls_name = self.__class__.__name__
        self.config_path = join(dirname(abspath(__file__)), 'config.json')
        # Logger
        self.log_init = LogInitializer()
        self.logger = self.log_init.initialize(self.config_path)



    # выводим атрибуты основного класса (стартового)
    def print_main(self) -> None:
        """
        Выводит атрибуты основного класса (стартового) и записывает их в лог

        Args:
            self: Экземпляр класса

        Returns:
            None
        """        
        
        # Создаем сообщение
        msg = (
            f"\nStarted at {strftime('%X')}\n"
            f'[{__name__}|{self.cls_name}] countInstance: [{self.countInstance}]\n'
            f'platform: [{platform}]\n'
            f'\nAttributes:\n'
            )
        # Атрибуты, которые будут выводиться
        attributes_to_print = [
            'abspath',
            'cls_name',
            'config_path',
            'config',
            'folder_swords',
            'pattern_name_swords',
            'replace_dict',
            'punct',
            'log_init',
            'logger',
            'srt_file',
            'sysmethods',
            'path_swords',

        ]
        # Выводим атрибуты с порядковыми номерами
        total_attributes = len(attributes_to_print)
        msg += f"Всего атрибутов {total_attributes}\n"

        for index, attr in enumerate(attributes_to_print, start=1):
            # Получаем значение атрибута или выводим "Attribute not found", 
            # если атрибут отсутствует
            value = getattr(self, attr, "Attribute not found")  
            msg += f"{index}. {attr}: {value}\n"        
        
        # Выводим сообщение
        print(msg)
        # Записываем сообщение в лог
        self.logger.log_info(msg)


    # выводим атрибуты объекта
    def print_class(self) -> None:
        """
        Выводит атрибуты вспомогательного класса и записывает их в лог

        Args:
            self: Экземпляр класса

        Returns:
            None
        """        
        
        # Создаем сообщение
        msg = (
            f"\nStarted at {strftime('%X')}\n"
            f'[{__name__}|{self.cls_name}] countInstance: [{self.countInstance}]\n'
            f'platform: [{platform}]\n'
            f'\nAttributes:\n'
            )
        # Атрибуты, которые будут выводиться
        attributes_to_print = [
            'abspath',
            'cls_name',
            'config_path',
            'log_init',
            'logger',

        ]

        # Выводим атрибуты с порядковыми номерами
        total_attributes = len(attributes_to_print)
        msg += f"Всего атрибутов {total_attributes}\n"

        for index, attr in enumerate(attributes_to_print, start=1):
            # Получаем значение атрибута или выводим "Attribute not found", 
            # если атрибут отсутствует
            value = getattr(self, attr, "Attribute not found")  
            msg += f"{index}. {attr}: {value}\n"        
        
        # Выводим сообщение
        print(msg)
        # Записываем сообщение в лог
        self.logger.log_info(msg)








