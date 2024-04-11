
from typing import Optional
from os.path import join, dirname
#
from app_env.app_init import LogInit

class BaseClass(LogInit):
    countInstance=0

    def __init__(self, config_file: Optional[str] = 'config.json'):
        super().__init__()

        # переназначаем родительский атрибут cls_name 
        self.cls_name = self.__class__.__name__
        
        # Config
        self.config_file = config_file
        self.config_path = join(dirname(self.entry_point), self.config_file)

        # Logger
        self.log_init = LogInit()
        self.logger = self.log_init.making_logger(self.config_path, self.cls_name)

        




