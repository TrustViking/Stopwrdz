#!/usr/bin/env python3 
#
from asyncio import run 
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlShutdown
from logging import getLevelName
from time import strftime
from os.path import basename
from sys import platform, argv, path
from psutil import virtual_memory
from typing import Coroutine
from argparse import ArgumentParser
from sqlalchemy.engine.result import Row
#
from bot_env.create_obj4bot import dp, bot
from bot_env.mod_log import Logger
from handlers.client import  Handlers4bot

#
#
class Telega:
    """Modul for TELEGRAM"""
    countInstance=0
    #
    def __init__(self, 
                 folder_swords='swords',
                 pattern_name_swords='swords_',
                 folder_logfile = 'logs',
                 logfile='telega_log.md',  
                 loglevel='DEBUG',
                 ):
        Telega.countInstance += 1
        self.countInstance = Telega.countInstance
        self.cls_name = self.__class__.__name__
        self.bot=bot
        self.dp=dp
        self.folder_logfile = folder_logfile
        self.logfile=logfile
        self.loglevel=loglevel
        self.folder_swords = folder_swords
        self.pattern_name_swords = pattern_name_swords
        # Разбор аргументов
        self._arg_parser()
        # Logger
        self.logger = Logger(self.folder_logfile, self.logfile, self.loglevel)
        # Client
        self.client = Handlers4bot(logger=self.logger, 
                                   folder_swords = self.folder_swords,
                                   pattern_name_swords = self.pattern_name_swords,
                                   )
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
            'bot',
            'dp',
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
    # добавление аргументов строки
    def _arg_added(self, parser: ArgumentParser):
        # Добавление аргументов
        parser.add_argument('-fs', '--folder_swords', type=str, help='Папка для файлов стоп-слов')
        parser.add_argument('-ns', '--pattern_name_swords', type=str, help='Шаблон имени файла стоп-слов')
        parser.add_argument('-fl', '--folder_logfile', type=str, help='Папка для логов')
        parser.add_argument('-lf', '--logfile', type=str, help='Имя журнала логгирования')
        parser.add_argument('-ll', '--loglevel', type=str, help='Уровень логгирования')

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
            # если из командной строки, то надо через инт
            # self.loglevel=int(args.loglevel) # (CRITICAL, ERROR, WARNING,INFO, DEBUG)
        
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
#
    # обертка для безопасного выполнения методов
    # async def safe_execute(self, coroutine: Callable[..., Coroutine[Any, Any, T]]) -> T:
    async def safe_await_execute(self, coroutine: Coroutine, name_func: str = None):
        if not coroutine:
            print(f'\n[Telega safe_await_execute] coroutine is {coroutine}')
            return None
        try:
            return await coroutine
        except Exception as eR:
            print(f'\nERROR[Telega {name_func}] ERROR: {eR}') 
            self.logger.log_info(f'\nERROR[Telega {name_func}] ERROR: {eR}') 
            return None

    ### запускаем клиент бот-телеграм
    async def client_work(self):
        await self.safe_await_execute(self.client.register_handlers_client(), 'client_work')            

    # отправляем сообщение
    async def send_msg(self, row: Row, msg: str):
        chat_id = str(row.chat_id)
        username=str(row.username)
        message = await self.safe_await_execute(self.bot.send_message(chat_id=chat_id, text=msg), 'send_msg')       
        if not message:
                print(f'\n[Telega send_msg] не удалось отправить пользователю [{username}] сообщение')
                return None
        return message  

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


# MAIN **************************
async def main():
    # Создаем экземпляр класса Start
    # создаем объект и в нем регистрируем хэндлеры Клиента
    telega=Telega()  
    telega.log_memory() # логирование информации о памяти
    telega.system_status() # выводим состояние системы
    # регистрируем обработчики
    await telega.client_work()
    drop_pending_updates = await telega.bot.delete_webhook(drop_pending_updates=True)
    print(f'\n[telega main] сбросили ожидающие обновления: [{drop_pending_updates}]')
    # обработчики
    await telega.dp.start_polling(telega.bot)
    print(f'\n[telega main] закончили start_polling...')
    #
#
if __name__ == "__main__":
    run(main())


