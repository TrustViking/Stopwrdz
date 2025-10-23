
from typing import Optional
from sys import argv
from os.path import join, isfile, basename, dirname

from app_env.base_class import BaseClass


class Vocabs(BaseClass):
    """
    Класс Vocabs предназначен для работы со словарями стоп-слов на разных языках.
    """    
    countInstance=0
    #
    def __init__(self):
        super().__init__()

        Vocabs.countInstance += 1
        self.countInstance = Vocabs.countInstance

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__

        # config
        self.config = self.read_config(self.config_path)
        self.folder_vocabs = self.config.get('folder_vocabs')
        self.pattern_name_vocab = self.config.get('pattern_name_vocab')
        # создаем рабочий путь к папке, где хранятся файлы словари стоп-слов на разных языках
        self.path_vocab_pattern = join(dirname(argv[0]), self.folder_vocabs, self.pattern_name_vocab)


    def form_path_dictionary_language(self, language: str)-> Optional[str]:
        """
        Формирует путь к словарю для определенного языка.

        Args:
            language (str): Язык, для которого формируется путь к словарю.

        Returns:
            str: Полный путь к словарю для указанного языка.
        """        

        name_method = self.get_current_method_name()

        # формируем путь к словарю исходя из определенного языка титров
        path_vocab = self.path_vocab_pattern+language.upper()+'.txt'

        if isfile(path_vocab):
            msg = (
                    f'\n[{self.cls_name}|{name_method}]'
                    f'\nПуть к словарю: [{dirname(path_vocab)}]'
                    f'\nФайл словаря: [{basename(path_vocab)}]'
                    )
            print(msg)

        else: 
            msg = (
                    f'\n*ERROR [{self.cls_name}|{name_method}]'
                    f'\n*Это ошибочный полный путь к словарю'
                    f'\n*Путь: [{dirname(path_vocab)}]'
                    f'\n*Словарь: [{basename(path_vocab)}]'
                    )
            print(msg)
            self.logger.error(msg)
            return None

        return path_vocab







