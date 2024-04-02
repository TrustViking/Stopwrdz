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
        parser.add_argument('-fs', '--folder_swords', type=str, help='Folder for stop-word files')
        parser.add_argument('-ns', '--pattern_name_swords', type=str, help='Pattern name for stop-word files')
        parser.add_argument('-fl', '--folder_logfile', type=str, help='Folder for log files')
        parser.add_argument('-lf', '--logfile', type=str, help='Log file name')
        parser.add_argument('-ll', '--loglevel', type=str, help='Logging level')
    
    # Разбор аргументов строки
    def _arg_parser(self):
        # Инициализация парсера аргументов
        parser = ArgumentParser()
        # добавление аргументов строки
        self._arg_added(parser)
        args = parser.parse_args()
        
        if args.folder_logfile: 
            self.folder_logfile=args.folder_logfile
        
        if args.logfile: 
            self.logfile=args.logfile
        
        if args.loglevel: 
            self.loglevel=getLevelName(args.loglevel.upper()) # (CRITICAL, ERROR, WARNING,INFO, DEBUG)
            print(f'self.loglevel: [{self.loglevel}]')
        
        if args.folder_swords: 
            self.folder_swords=args.folder_swords
        
        if args.pattern_name_swords: 
            self.pattern_name_swords=args.pattern_name_swords

    # логирование информации о памяти
    def log_memory(self):
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

    # обертка для безопасного выполнения методов
    # async def safe_execute(self, coroutine: Callable[..., Coroutine[Any, Any, T]]) -> T:
    async def safe_await_execute(self, coroutine: Coroutine, name_func: str = None):
        if not coroutine:
            print(f'\n[Start safe_await_execute] coroutine is {coroutine}')
            return None
        try:
            return await coroutine
        except Exception as eR:
            print(f'\nERROR[Start {name_func}] ERROR: {eR}') 
            self.logger.log_info(f'\nERROR[Start {name_func}] ERROR: {eR}') 
            return None


    # Асинхронная функция для запуска скрипта
    async def subprocess_script(self, script):
        self.logger.log_info(f'[Start subprocess_script] start script: {script}')
        print(f'\n[Start subprocess_script] start script: {script}')
        # Example:
        # await asyncio.create_subprocess_shell("ls -l > output.txt")
        # await asyncio.create_subprocess_exec("ls", "-l")
        try:
            # Используем asyncio для асинхронного запуска скрипта
            process = await self.safe_await_execute(create_subprocess_shell(script), 'run_script')
            if not process:
                print(f'\n[Start subprocess_script] нет процесса!!! process: {process}')
                return None 
        except Exception as eR:
            print(f'\nERROR[Start making_subprocess_script] ERROR: {eR}') 
            self.logger.log_info(f'\nERROR[Start subprocess_script] ERROR: {eR}') 
            return None
        await process.wait()

    # выводим состояние системы
    def system_status(self):
        print(f'\nСтарт приложения...\n') 
        file_start = basename(argv[0])
        path_start = path[0]
        msg = (
            f'File: [{file_start}]\n'
            f'Path: [{path_start}]\n'
            f'Data memory:'
                )
        print(msg)
        memory = virtual_memory()
        for field in memory._fields:
            print(f"{field}: {getattr(memory, field)}")    


    # Список скриптов с аргументами для запуска
    def scripts_args(self):
        args_bot_telega=' '
        
        if self.folder_swords: 
            args_bot_telega+=f'--folder_swords {self.folder_swords} '

        if self.pattern_name_swords: 
            args_bot_telega+=f'--pattern_name_swords {self.pattern_name_swords} '
        
        if self.folder_logfile:
            folder_logfile_arg=f'--folder_logfile {self.folder_logfile} '
            args_bot_telega+=folder_logfile_arg

        if self.logfile:
            log_file_arg=f'--logfile {self.logfile} '
            args_bot_telega+=log_file_arg

        if self.loglevel:
            log_level_arg=f'--loglevel {self.loglevel} '
            args_bot_telega+=log_level_arg

        print(f'\n[Start scripts_args] \nargs_bot_telega: {args_bot_telega}')
            
        # создаем командную строку для bot_telega.py
        full_path_telega = join(path[0], 'bot_telega.py')
        if not isfile(full_path_telega):
            print(f'\nERROR [Start scripts_args] Нет файла: {full_path_telega}')
            return None
        #
        script_telega_args = 'python ' + full_path_telega + args_bot_telega
        print(f'\n[Start making_scripts_args] script_telega: {script_telega_args}')

        return [
            script_telega_args,
                    ]

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



