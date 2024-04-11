


import shutil
from os.path import basename, join, abspath, dirname, getmtime, isdir, isfile
from os import makedirs, listdir, remove
from sys import platform, argv, path
from typing import Coroutine, List, Optional, Dict, Union, Any
from time import sleep, strftime
from datetime import datetime as dt
from json import load, JSONDecodeError
#
# from app_env.decorators import safe_execute
from app_env.base_class import BaseClass


class Prints(BaseClass):
    """
    Class for displaying class attributes and other debugging information on the screen
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Prints.countInstance += 1
        self.countInstance = Prints.countInstance
    
    @classmethod
    # метод print_class() принимает экземпляр класса в качестве аргумента
    # def print_class(self, instance: BaseClass) -> None:
    def print_class(cls, instance: BaseClass) -> None:
        """
        Выводит атрибуты вспомогательного класса и записывает их в лог

        Args:
            instance: Экземпляр класса BaseClass

        Returns:
            None
        """   

        # Счетчик вызовов метода
        if not hasattr(cls, 'call_count'):
            cls.call_count = 0
        cls.call_count += 1

        # @safe_execute(logger=instance.logger, name_method=f'[{instance.__class__.__name__}]')
        def  _print_class():
            # Создаем первую часть сообщения
            msg = (
                f"\nStarted at {strftime('%X')}\n"
                f'[{cls.__name__}|{instance.cls_name}] countInstance: [{instance.countInstance}]\n'
                f'Call count classmethod print_class: [{cls.call_count}]\n'  # Добавляем показания счетчика
                f'Platform: [{platform}]'
                f'\nAttributes:\n'
                )
            # Получаем список атрибутов объекта
            attributes = dir(instance)

            # Удаляем "магические" атрибуты, начинающиеся и заканчивающиеся двумя подчеркиваниями
            attributes = [attr for attr in attributes if not attr.startswith('__') and not attr.endswith('__')]
            # print(f'\nAll attributes: {attributes}\n')

            # Формируем сообщение с атрибутами и их значениями
            for index, attr in enumerate(attributes, start=1):
                # Получаем значение атрибута или выводим "Атрибут не найден", 
                # если атрибут отсутствует
                value = getattr(instance, attr, "Attribute not found") 
                # дописываем в первую часть сообщения 
                msg += f"{index}. {attr}: {value}\n"        
            
            # Выводим сообщение
            # print(msg)

            # Записываем сообщение в лог
            # instance.logger.info(msg)
        return _print_class()






