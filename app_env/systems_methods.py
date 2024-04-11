

from sys import argv
from typing import Optional
from app_env.base_class import BaseClass


class SysMethods(BaseClass):
    """
    Класс `SysMethods` предназначен для работы с командной строкой.

    Attributes:
        countInstance (int): Статический атрибут для подсчета количества экземпляров класса.
    """
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        SysMethods.countInstance += 1
        self.countInstance = SysMethods.countInstance

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__
        

    # Разбор аргументов строки
    def args(self) -> Optional[str]:
        """
        Получает аргумент командной строки, содержащий путь к файлу субтитров.

        Если количество аргументов не равно 2 (только имя скрипта и путь к файлу), 
        то вызывается исключение.

        Args:
            self: Экземпляр класса.

        Returns:
            str: Путь к файлу субтитров, если аргумент передан корректно.
            None: Если количество аргументов некорректно.
        """
        name_method = self.get_current_method_name()

        # Проверяем количество аргументов командной строки
        if len(argv) != 2:
            # Если количество аргументов не равно 2, вызываем исключение
            msg = f'\n*ERROR [{self.cls_name}|{name_method}] ERROR: Not full path to the title file with .srt extension'
            self.logger.error(msg)
            raise Exception(msg)
        # Возвращаем второй аргумент командной строки (путь к файлу субтитров)
        return argv[1]




