
from logging import getLevelName, getLogger, Formatter, FileHandler 
from typing import Any
from os.path import join, dirname, exists
from os import makedirs
from sys import platform, argv, path
from time import time, strftime

class Logger:

    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    countInstance=0

    def __init__(self,
                folder_logfile='logs', 
                logfile='log.md', 
                loglevel=10,
                 ):
        """
        Конструктор класса Logger.

        Аргументы:
        - log_file: Имя файла логирования. По умолчанию None.
        - log_level: Уровень логирования. По умолчанию logging.INFO.

        Возможные уровни логирования:
        - DEBUG: Детальная отладочная информация.
        - INFO: Информационные сообщения.
        - WARNING: Предупреждения.
        - ERROR: Ошибки, которые не приводят к прекращению работы программы.
        - CRITICAL: Критические ошибки, которые приводят к прекращению работы программы.
        """
        Logger.countInstance += 1
        self.countInstance = Logger.countInstance

        self.cls_name = self.__class__.__name__

        self.logfile=logfile
        self.folder_logfile=folder_logfile
        self.loglevel=getLevelName(loglevel)
        self.path_to_logfile = join(path[0], self.folder_logfile, self.logfile)
        self.create_directory(self.path_to_logfile)
        self.logger = self.setup_logger(self.loglevel, self.path_to_logfile)
        self._print()


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
            'path_to_logfile',
            'logger',
        ]

        for attr in attributes_to_print:
            # "Attribute not found" будет выведено, если атрибут не существует
            value = getattr(self, attr, "Attribute not found")  
            msg += f"{attr}: {value}\n"

        print(msg)
        # self.logger.log_info(msg)


    def create_directory(self, path):
        """
        Создает директорию, если она не существует.
        """
        directory = dirname(path)
        # print(f'\n[Logger create_directory] directory: {directory}')
        if not exists(directory):
            makedirs(directory) 

    def setup_logger(self, log_level: int or str, path_logfile: str):
        """
        Настраивает логгер.

        Возвращает:
        - logger: Объект логгера.
        """
        
        nameToLevel = {
            'CRITICAL': Logger.CRITICAL,
            'FATAL': Logger.FATAL,
            'ERROR': Logger.ERROR,
            'WARN': Logger.WARNING,
            'WARNING': Logger.WARNING,
            'INFO': Logger.INFO,
            'DEBUG': Logger.DEBUG,
            'NOTSET': Logger.NOTSET,
        }

        levelToName = {
            Logger.CRITICAL: 'CRITICAL',
            Logger.ERROR: 'ERROR',
            Logger.WARNING: 'WARNING',
            Logger.INFO: 'INFO',
            Logger.DEBUG: 'DEBUG',
            Logger.NOTSET: 'NOTSET',
        }

        if isinstance(log_level, int):
            loglevel = log_level
            print(f'\n[{__name__}|{self.cls_name}] loglevel: [{loglevel}]')
        elif isinstance(log_level, str):
            if log_level not in nameToLevel:
                print(f'\n[{__name__}|{self.cls_name}] ERROR log_level: [{log_level}] not in nameToLevel')
                return None
            print(f'\n[{__name__}|{self.cls_name}] loglevel: [{log_level}]')
            loglevel = nameToLevel[log_level]
        else:
            print(f'\n[{__name__}|{self.cls_name}] ERROR log_level: [{log_level}] is not int or str')
            return None
        
        # хэндлер
        file_handler = FileHandler(path_logfile)
        file_handler.setLevel(loglevel)
        formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # создаем логгер
        logger = getLogger(__name__)
        # устанавливаем уровень логгирования
        logger.setLevel(loglevel)
        # добавляем хэндлер в логгер
        logger.addHandler(file_handler)
        #
        return logger

    def log_info(self, message: Any):
        """
        Записывает информационное сообщение в лог.

        Аргументы:
        - message: Сообщение для записи в лог.
        """
        self.logger.info(message)


