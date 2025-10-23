
from logging import Logger
from functools import wraps
from typing import Callable, Any
#

# декоратор для безопасного выполнения методов
def safe_execute(logger: Logger, name_method: str = None):
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as eR:
                msg = f'\n*ERROR[{name_method}]: {str(eR)}'
                print(msg)
                logger.error(msg) 
                return None
        return wrapper
    return decorator
