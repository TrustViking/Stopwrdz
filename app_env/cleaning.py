

from os.path import join, getmtime, dirname, splitext
from os import listdir, remove
from typing import Union
from datetime import datetime as dt

from app_env.base_class import BaseClass


class Cleaning(BaseClass):
    """
    Класс `Cleaning` предназначен для удаления файлов и папок из указанных директорий, 
    которые старше определенного срока.
    """

    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Cleaning.countInstance += 1
        self.countInstance = Cleaning.countInstance
        
        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__


    # удаляем старые журналы логгирования
    def delete_logs(self, 
                    config_path: str, 
                    time_delete: int = 86400,
                    ) -> Union[int, str]:
        """
        Метод для удаления файлов журналов логгирования, 
        которые старше определенного срока.

        Args:
            self: Экземпляр класса.
            config_path (str): Путь к файлу конфигурации.
            time_delete (int, optional): Время (в секундах), после которого файлы считаются устаревшими 
                                        и могут быть удалены. По умолчанию 86400 секунд (24 часа).

        Returns:
            Union[int, str]: Возвращает количество удаленных лог-файлов (int) 
                            или сообщение о том, что лог-файлы не были удалены (str).

        Raises:
            Exception: Если не удалось прочитать файл конфигурации.

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
        
        # создаем полный путь к папке хранения лог-файлов
        folder_logfile = config.get('folder_logfile')
        path_logdir = join(dirname(self.entry_point), folder_logfile)
        
        # выделяем шаблон имени лог-файлов
        logfile = config.get('logfile')
        base_name, extension = splitext(logfile)
        
        # множество имен лог-файлов 
        set_nfile = set(listdir(path_logdir))

        # Фильтрация имен лог-файлов по шаблону base_name
        filtered_names = [name for name in set_nfile if base_name in name]   
        msg = (
                f'\n[{self.cls_name}|{name_method}]'
                f'\nИмена [{len(filtered_names)}] файлов логгов:'
                )
        for i, names in enumerate(filtered_names, start=1):
            msg += f"\n{i}. {names}"        
        print(msg)

        # Создание списка полных путей на базе отфильтрованных имен файлов
        filtered_paths = [join(path_logdir, name) for name in filtered_names]  

        # текущее время
        current_time = dt.now().timestamp()
        
        # список для хранения путей к удаленным логгам
        deleted_logs = []  
        
        for full_path in filtered_paths:
            
            # время последнего изменения лога
            file_mod_time = getmtime(full_path)
            
            # если лог старше time_delete
            if current_time - file_mod_time > time_delete:
                # удаляем лог-файл
                remove(full_path)
                # записываем полный путь удаленного лог-файла в список
                deleted_logs.append(full_path)
        
        if not deleted_logs:
            msg = (
                    f'\n[{self.cls_name}|{name_method}]'
                    f'\nУдаленных логгов нет'
                    f'\ndeleted_logs: [{deleted_logs}]'
                    )
            return str(0)
        else: 
            msg = (
                    f'\n[{self.cls_name}|{name_method}]'
                    f'\nУдаленные логги:'
                    )
            for i, names in enumerate(deleted_logs, start=1):
                msg += f"\n{i}. {names}"        
            print(msg)
        
            return len(deleted_logs)



