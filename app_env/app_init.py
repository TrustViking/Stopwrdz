

from typing import Optional, Dict
from logging import Logger, DEBUG, getLogger, Formatter, FileHandler 
from sys import argv
from os.path import join, isfile, abspath, dirname, splitext
from json import load, JSONDecodeError
from os import makedirs
import inspect
from datetime import datetime



class ConfigInit:
    def __init__(self):
        self.cls_name = self.__class__.__name__

    def get_current_method_name(self):
        """
        Возвращает имя текущего метода.
        """
        return inspect.stack()[1].function

    # если файл содержит смешанный вариант данных как int так и  str, 
    # то возврат Optional[Dict[str, Union[int, str]]]
    def read_config(self, config_path: str) -> Optional[Dict[str, str]]:
        """
        Считывает конфигурационные данные из файла JSON.

        Аргументы:
        - config_path: str. Путь к файлу конфигурации.

        Возвращаемое значение:
        - Optional[Dict[str, str]]. Словарь с конфигурационными данными 
            или None, если произошла ошибка.
        """
        name_method = self.get_current_method_name()

        if not isfile(config_path):
            msg = f'\nERROR [{self.cls_name}|{name_method}]] not exist config_path: {config_path}' 
            print(msg)
            return None
        
        try:
            with open(config_path, 'r') as f:
                return load(f)
        
        except JSONDecodeError as e:
            msg = f"\nERROR [{self.cls_name}|{name_method}] Error decoding JSON config: {e}"
            print(msg)
            return None


class LogInit(ConfigInit):
    def __init__(self):
        """
        Инициализатор класса LogInit
        - `%(name)s`: Имя логгера (канал логирования)
        - `%(levelno)s`: Числовой уровень логирования для сообщения (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - `%(levelname)s`: Текстовый уровень логирования для сообщения ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        - `%(pathname)s`: Полный путь к исходному файлу, где был выполнен вызов логирования (если доступно)
        - `%(filename)s`: Имя файла в пути
        - `%(module)s`: Название модуля (часть имени файла)
        - `%(lineno)d`: Номер строки исходного кода, где был выполнен вызов логирования (если доступно)
        - `%(funcName)s`: Название функции
        - `%(created)f`: Время создания записи лога (возвращаемое значение функции time.time())
        - `%(asctime)s`: Текстовое представление времени создания записи лога
        - `%(msecs)d`: Миллисекундная часть времени создания записи лога
        - `%(relativeCreated)d`: Время в миллисекундах относительно момента загрузки модуля логирования (обычно время запуска приложения)
        - `%(thread)d`: Идентификатор потока (если доступно)
        - `%(threadName)s`: Название потока (если доступно)
        - `%(process)d`: Идентификатор процесса (если доступно)
        - `%(message)s`: Результат вызова record.getMessage(), вычисленный непосредственно в момент отправки записи лога

        """
        super().__init__()

        ##### точка входа скрипта
        self.entry_point = abspath(argv[0])

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__


    def making_logger(self, config_path: str, pattern_name_logger: str) -> Logger:
        """
        Создает и настраивает логгер на основе конфигурации.

        Аргументы:
        - config_path (str): Путь к файлу конфигурации.

        Возвращает:
        - logger (Logger): Настроенный логгер.

        Raises:
        - Exception: Если не удалось прочитать конфигурацию или создать логгер.
        """        
        name_method = self.get_current_method_name()

        # конфигурация
        config = self.read_config(config_path)
        if config is None:
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Failed to read configuration [{config_path}]'
                    )
            print(msg)
            raise Exception(msg)
        
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%Y-%m-%d_%H-%M-%S')
        
        # имя логгера
        name_logger = f"{pattern_name_logger}_{formatted_datetime}"
        
        # логгер
        logger = getLogger(name_logger)
        # уровень логгирования
        loglevel = config.get('loglevel', DEBUG)
        logger.setLevel(loglevel)
        
        # создаем полный путь к лог файлу
        folder_logfile = config.get('folder_logfile')
        logfile = config.get('logfile')
        # Разделение имени файла на основное имя и расширение
        base_name, extension = splitext(logfile)
        logfile = f"{formatted_datetime}_{base_name}_{pattern_name_logger}{extension}"
        path_logfile = join(dirname(self.entry_point), folder_logfile, logfile)

         # Создание директории, если она не существует
        _ = [makedirs(path, exist_ok=True) for path in [dirname(path_logfile)]]

        # хэндлер
        file_handler = FileHandler(path_logfile, encoding='utf-8')
        formatter = Formatter('\n%(asctime)s - [%(name)s] - %(levelname)s - %(funcName)s: %(message)s')
        file_handler.setFormatter(formatter)
        
        # добавляем хэндлер в логгер
        logger.addHandler(file_handler)

        return logger

