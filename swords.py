#!/usr/bin/env python3
#
from asyncio import create_subprocess_shell, gather, run 
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlShutdown
from logging import getLevelName
from time import strftime
from os.path import basename, join, isfile
from sys import platform, argv, path
from psutil import virtual_memory
from typing import Coroutine
from argparse import ArgumentParser
from bot_env.mod_log import Logger

class Start:
    """Module for START"""
    countInstance=0
    #
    def __init__(self, 
                 folder_swords='vocab_swords',
                 pattern_name_swords='swords_',
                 folder_logfile = 'logs',
                 logfile='log.md', 
                 loglevel='DEBUG',
                 ):
        Start.countInstance += 1
        self.countInstance = Start.countInstance
        #
        self.cls_name = self.__class__.__name__
        self.folder_logfile = folder_logfile
        self.logfile=logfile
        self.loglevel=loglevel
        self.folder_swords = folder_swords
        self.pattern_name_swords = pattern_name_swords
        # Разбор аргументов командной строки
        self._arg_parser()
        # Logger
        self.logger = Logger(self.folder_logfile, self.logfile, self.loglevel)
        self._print()

        #     
    # выводим № объекта
    def _print(self):
        msg = (
            f"\nStarted at {strftime('%X')}\n"
            f'[{__name__}|{self.cls_name}] countInstance: [{self.countInstance}]\n'
            f'platform: [{platform}]\n'
            f'\nAttributes:\n'
            )

        attributes_to_print = [
            'cls_name',
            'folder_logfile',
            'logfile',
            'loglevel',
            'folder_swords',
            'pattern_name_swords',
            'logger',
        ]

        for attr in attributes_to_print:
            # "Attribute not found" будет выведено, если атрибут не существует
            value = getattr(self, attr, "Attribute not found")  
            msg += f"{attr}: {value}\n"

        print(msg)
        self.logger.log_info(msg)
    # 
    # добавление аргументов командной строки
    def _arg_added(self, parser: ArgumentParser):
        # Добавление аргументов
        parser.add_argument('srt_file', type=str, help='Full path to the title file with .srt extension')


    # Разбор аргументов строки
    def _arg_parser(self):
        # Инициализация парсера аргументов
        parser = ArgumentParser()
        # добавление аргументов строки
        self._arg_added(parser)
        args = parser.parse_args()
        
        if args.srt_file:
            self.srt_file = args.srt_file
        else:
            raise Exception(f'\nERROR [Start] ERROR: Not full path to the title file with .srt extension')


# MAIN **************************
# Главная асинхронная функция
async def main():
    # Создаем экземпляр класса Start
    start = Start()
    start.log_memory() # логирование информации о памяти
    start.system_status() # выводим состояние системы
    #
    # Запускаем скрипты асинхронно
    scripts = start.scripts_args() # Список скриптов с аргументами для запуска
    tasks = [start.subprocess_script(script) for script in scripts]
    await gather(*tasks)

# Запускаем главную асинхронную функцию
if __name__ == "__main__":
    run(main())



