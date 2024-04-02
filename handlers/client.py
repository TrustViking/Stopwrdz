
import re
import os, sys
import chardet
from typing import Dict
from io import BytesIO
import string
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from aiogram import F
from aiogram.types.message import Message
from aiogram.types import BufferedInputFile
from aiogram.filters import Command
from bot_env.mod_log import Logger
from bot_env.create_obj4bot import bot, dp

class Handlers4bot:
    """
    Создаем для telegram-bot хэндлеры клиента:

    Аргументы:
    - logger: Logger
    """
    countInstance=0
    #
    def __init__(self, 
                 logger: Logger,
                 folder_swords,
                 pattern_name_swords,
                    ): 

        Handlers4bot.countInstance+=1
        self.countInstance=Handlers4bot.countInstance
        self.countHandlers=0
        self.folder_swords=folder_swords
        self.pattern_name_swords=pattern_name_swords
        self.bot=bot
        self.dp=dp
        # ℃ ∈ ☪
        self.replace_dict={'a': '@', 'e':'€', 'i':'!', 'o':'0', 's':'$', 'u':'и', 'w':'vv', 'r':'®', 'c':'©',
                           'а': '@', 'е':'€', 'и':'N', 'й':'N', 'о':'0', 'р':'₽'}
        self.path_swords = os.path.join(sys.path[0], folder_swords, self.pattern_name_swords)
        self.Logger = logger
        self.punct = ['!', '?', '"', '-', ',', '.', ':', ';']
        self._new_client()
        #
        #
    # New Client
    def _new_client(self):
        print(f'[_new_client] Client# {self.countInstance}')
        self.Logger.log_info(f'[_new_client] Client# {self.countInstance}')

    # New handlers
    def _new_handlers(self, name_handler=None):
        self.countHandlers+=1
        print(f'\n\n[_new_handlers] Handler {name_handler} # {self.countHandlers}')
        self.Logger.log_info(f'[_new_handlers] Handler# {self.countHandlers}')

    # асинхронная обертка для безопасного выполнения методов
    async def safe_await_execute(self, coroutine, name_func: str = None):
        try:
            return await coroutine
        except Exception as eR:
            print(f'\nERROR[Handlers4bot {name_func}] ERROR: {eR}') 
            self.Logger.log_info(f'\nERROR[Handlers4bot {name_func}] ERROR: {eR}') 
            return None

    # синхронная обертка для безопасного выполнения методов
    def safe_execute(self, func, name_func: str = None):
        try:
            return func
        except Exception as eR:
            print(f'\nERROR[VidCompar {name_func}] ERROR: {eR}') 
            self.Logger.log_info(f'\nERROR[VidCompar {name_func}] ERROR: {eR}') 
            return None

    # определяем кодировку файла
    def detect_file_encoding(self, file_path: str, name_func: str = None):
        try:
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
        except Exception as eR:
            print(f'\nERROR[Handlers4bot detect_file_encoding] ERROR: {eR}') 
            self.Logger.log_info(f'\nERROR[Handlers4bot detect_file_encoding] ERROR: {eR}') 
            return None
        # print(f'[Handlers4bot detect_file_encoding {name_func}] result: [{result}]')
        return result['encoding']
    
    # определяем кодировку буффера 
    def detect_buffer_encoding(self, buffer: BytesIO):
        result = self.safe_execute(chardet.detect(buffer.read()), 'detect_buffer_encoding')
        # print(f'[Handlers4bot detect_buffer_encoding] result: [{result}]')
        return result['encoding']

    def filtering_swords(self, file_path: str):
        """
        Загружает файл стоп-слов, убирает повторы и сортирует его
        с последующей записью на диск

        :param file_path: полный путь к файлу
        :return: полный путь к перезаписанному файлу
        """
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print(f'\nERROR [filtering_swords] Проверьте полный путь к файлу стоп-слов: {file_path}')
            return None
        
        # определяем кодировку файла стоп-слов
        encoding = self.detect_file_encoding(file_path, 'filtering_swords')
        print(f'\n[filtering_swords] кодировка [{encoding}] файла {file_path}')
        if not encoding:
            msg = f'\n[Handlers4bot filtering_swords] Не определили кодировку после фильтрации файла стоп-слов: {file_path}'
            print(msg)
            return None
        
        # Чтение файла в память
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                stop_words = f.read().splitlines()
        except Exception as eR:
            print(f'\nERROR[Handlers4bot filtering_swords read stop-words] ERROR: {eR}') 
            self.Logger.log_info(f'\nERROR[Handlers4bot filtering_swords read stop-words] ERROR: {eR}') 
            return None

        # Добавление вариантов слов с большой и маленькой буквы,
        # а также как есть (особенно для названий: YouTube...)
        case_sensitive_words = set()
        for word in set(filter(lambda x: x.strip(), stop_words)):
             # Проверка, состоит ли "слово" из нескольких слов
            if ' ' in word:
                continue  # Пропустить, если "слово" на самом деле фраза
            case_sensitive_words.add(word)
            case_sensitive_words.add(word.lower())
            case_sensitive_words.add(word.capitalize())            

        # Сортировка swords
        swords = sorted(case_sensitive_words)

        # запись swords в файл на диск
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                for word in swords:
                    f.write(f"{word}\n")
        except Exception as eR:
            print(f'\nERROR[Handlers4bot filtering_swords write stop-words] ERROR: {eR}') 
            self.Logger.log_info(f'\nERROR[Handlers4bot filtering_swords write stop-words] ERROR: {eR}') 
            return None
        
        return file_path
    
    # определяем язык текста
    # возвращаем строку 'en', 'ru', 'ro' or None
    def detection_lang(self, buf: BytesIO):
        buf.seek(0)
        # определяем кодировку буффера 
        encoding=self.detect_buffer_encoding(buf)
        print(f'\n[Handlers4bot detection_lang] Буфер в кодировке: {encoding}')

        buf.seek(0)
        text = [line.decode(encoding=encoding) for line in buf.readlines()]
        try:
            return detect(' '.join(text))
        except LangDetectException as eR:
            print(f'\nERROR[Handlers4bot detection_lang] LangDetectException: {eR}')
            self.Logger.log_info (f'\nERROR[Handlers4bot detection_lang] LangDetectException: {eR}')
            return None
        except UnicodeDecodeError as eU:
            error_message = f'\nERROR[Handlers4bot detection_lang] UnicodeDecodeError: {eU}'
            print(error_message)  # или self.Logger.log_info(error_message)
            return None

    def diction_swords(self, file_path: str, replace_dict: dict):
        """
        Загружает слова из файла и создает словарь стоп-слов и их замен.

        :param file_path: полный путь к файлу
        :param replace_dict: словарь для замены символов
        :return: словарь, где ключ - исходное слово, значение - измененное слово
        """
        word_dict = {}

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print(f'\nERROR [diction_swords] Проверьте полный путь к файлу стоп-слов')
            return None
        encoding = self.detect_file_encoding(file_path, 'diction_swords')
        print(f'\n[diction_swords] кодировка [{encoding}] файла {file_path}')
        try:
            
            with open(file_path, 'r', encoding=encoding) as f:
                for line in f:
                    # Убираем пробелы и переносы строк с обоих концов строки
                    word = line.strip()
                    
                    # Производим замену символов
                    replaced_word = "".join([replace_dict.get(char, char) for char in word])
                    
                    # Сохраняем в словаре
                    word_dict[word] = replaced_word
        
        except Exception as eR:
            print(f'\nERROR[Handlers4bot diction_swords] ERROR: {eR}') 
            self.Logger.log_info(f'\nERROR[Handlers4bot diction_swords] ERROR: {eR}') 
            return None
        return word_dict

    # обрабатывает команду пользователя - /start
    async def command_start(self, message: Message): 
        # await Form.first_video.set()
        msg = (f'Пришлите сюда файл с титрами на: \n'
               f'\n*английском*\, *русском*\ или *румынском*\ языке \n'
               f'\n_Другие языки пока не поддерживаются_\ \n')
        await self.bot.send_message(message.from_user.id, msg, parse_mode='MarkdownV2')  
    
    # обработчик любого сообщения, кроме  - /start
    # from_user: id=618894555 is_bot=False first_name='AAAAAAAA' last_name=None 
    # username='AAAA' language_code='ru' is_premium=None 
    # added_to_attachment_menu=None can_join_groups=None 
    # can_read_all_group_messages=None supports_inline_queries=None    
    async def any2start(self, message: Message):
        _msg=(f'Прислали: {message.content_type}\n'
              f'from_user.id: {message.from_user.id}\n'
              )
        await self.bot.send_message(message.from_user.id, text=_msg)
        msg = (f'Наберите команду [/start] для начала')
        await self.bot.send_message(message.from_user.id, msg)


    def replace_swords(self, buf: BytesIO, diction: Dict[str, str]) -> BytesIO:
        new_buf = BytesIO()
        buf.seek(0)

        # Проходим по каждой строке в буфере
        for line in buf.readlines():
            decoded_line = line.decode('utf-8')
            puncts=[] # список кортежей
            new_elements = [] # список символов строки
            for i, element in enumerate(decoded_line):
                if element in self.punct:
                    puncts.append((i, element))
                else:
                    new_elements.append(element)
            
            print(f'\npuncts: {puncts}')
            print(f'new_elements: {new_elements}')
            
            # строка из списка без пунктуации
            new_line = ''.join(new_elements)
            print(f'new_line: {new_line}')

            # Разбиваем по пробелам строку на список слов 
            words = [word.strip() for word in new_line.split()] 
            print(f'words: {words}')
            
            # проверяем каждое слово и заменяем на слово из словаря
            new_words = [diction.get(word, word) for word in words]
            print(f'new_words: {new_words}')
            
            # соединяем через пробел список слов в строку
            new_string = ' '.join(new_words)
            print(f'new_string: {new_string}')

            # строку переводим в список символов
            symbols = list(new_string)

            # добавляем к символам пунктуацию
            if puncts:
                for i, punct in puncts:
                    symbols.insert(i, punct)
            
            string_puncts = ''.join(symbols)
            print(f'string_puncts: {string_puncts}')
            
            # Собираем список символов обратно в строку
            new_line = ''.join(symbols).encode('utf-8')
            new_buf.write(new_line + b'\n')

        return new_buf


    # отправляем буфер-документ
    async def send_srt_file(self, chat_id: str, buffer: BytesIO, nfile: str):
        # Переход к началу буфера
        buffer.seek(0)
        
        message_file = await self.safe_await_execute(
                        self.bot.send_document(chat_id, BufferedInputFile(buffer.read(), filename=nfile), caption='Файл титров без стоп-слов'),'send_srt_file')
        return message_file

    # отправляем сообщение
    async def send_msg(self, chat_id: str, msg: str):
        message = await self.safe_await_execute(
                        self.bot.send_message(chat_id=chat_id, 
                                              text=msg), 'send_msg')
        return message       

    ## обработчик файла титров
    async def process_title(self, message: Message):
        self._new_handlers('process_title')
        #
        doc_file_id=str(message.document.file_id)
        number = message.document.file_size
        if number: 
            file_size_format = f"{number:,}".replace(",", " ")
        mime = str(message.document.mime_type).split('/')[1]
        print(f'\n[Handlers4bot process_title] \nfile_id: {doc_file_id} \nmime: {mime}')
        #
        msg = (f'Файл с титрами:\n'
               f'file_size: {file_size_format} bytes\n'
               f'mime_type: {mime}\n'
               f'Начинаю обрабатывать файл...'
               )
        await self.bot.send_message(message.from_user.id, msg)
        #
        doc = message.document if message else None
        if not doc:
            msg = (f'\n[Handlers4bot process_title] Документ не получил. \n'
                   f'Отправьте документ еще раз.')
            print(msg)
            await self.bot.send_message(message.from_user.id, msg)            
            return None
        
        # Загрузить документ в буфер
        buf = await self.safe_await_execute(self.bot.download(file=doc_file_id, destination=BytesIO(), timeout=120), 'process_title file_doc.download')   
        if not buf:
            print(f"\n[Handlers4bot process_title] document don't saved in buf. BUF: {buf}")
            self.Logger.log_info(f"\n[Handlers4bot process_title] document don't saved in buf. BUF: {buf}")
            return None 
        # 
        # начало буфера
        buf.seek(0)
        language = self.detection_lang(buf)
        print(f'\n[Handlers4bot process_title] language: {language}')
        if not language:
            msg = f'\n[Handlers4bot process_title] Не определили язык титров language: {language}'
            print(msg)
            await self.send_msg(message.from_user.id, msg)
            return None

        # файл стоп-слов, убираем повторы, сортируем и перезаписываем
        full_path_swords = self.safe_execute(self.filtering_swords(self.path_swords+language.upper()+'.txt'), 'process_title filtering_swords')
        if not full_path_swords:
            msg = f'\n[Handlers4bot process_title] Не отфильтровали файл стоп-слов full_path_swords: {full_path_swords}'
            print(msg)
            await self.send_msg(message.from_user.id, msg)
            return None
        
        # оперделяем кодировку файла стоп-слов
        encoding = self.detect_file_encoding(full_path_swords, 'diction_swords')
        if not encoding:
            msg = f'\n[Handlers4bot process_title] Не определили кодировку после фильтрации файла стоп-слов: {full_path_swords}'
            print(msg)
            await self.send_msg(message.from_user.id, msg)
            return None
        
        # создаем словарь стоп-слов и их замен
        swords = self.safe_execute(self.diction_swords(full_path_swords, self.replace_dict), 'process_title diction_swords')
        # print(f'swords: {swords}') 
        if not swords:
            msg = (f'\n[Handlers4bot process_title] Не создали словарь стоп-слов {swords} \n'
                  f'на языке {language}') 
            print(msg)
            await self.send_msg(message.from_user.id, msg)
            return None
        
        # новый файл титров
        new_buf = self.safe_execute(self.replace_swords(buf, swords), 'process_title replace_swords')
        size_in_bytes = new_buf.getbuffer().nbytes
        print(f'\nНовый файл титров содержит {size_in_bytes} байтов')
        if not new_buf:
            msg = (f'\n[Handlers4bot process_title] Не создали новый файл титров {new_buf} \n'
                  f'на языке {language}')
            print(msg)
            await self.send_msg(message.from_user.id, msg)
            return None
        
        # отправляем буфер-документ
        nfile='swords_title.srt' # имя файла новых титров
        msg = await self.safe_await_execute(self.send_srt_file(message.from_user.id, new_buf, nfile), 'process_title send_srt_file')
        if msg: 
            print(f'\n[Handlers4bot process_title] {msg.date} [{msg.from_user.username}] отправил [{msg.chat.username}] \nновый файл [{msg.document.file_name}] с титрами без стоп-слов')
        else: 
            msg = f'\n[Handlers4bot process_title] Новый файл с титрами без стоп-слов НЕ ОТПРАВИЛИ'
            print(msg)
            await self.send_msg(message.from_user.id, msg)
            return None

    ### регистрация хэндлеров
    async def register_handlers_client(self):
        # обрабатываем нажатие кнопки СТАРТ 
        # self.dp.register_message_handler(self.command_start, Command('start'))
        self.dp.message.register(self.command_start, Command('start'))
        # обрабатываем первое видео 
        # self.dp.callback_query.register(self.process_title, content_types=ContentType.DOCUMENT)
        self.dp.message.register(self.process_title, F.document)
        # любые сообщения и на старт
        # self.dp.register_message_handler(self.any2start, content_types=ContentType.ANY, state='*')
        self.dp.message.register(self.any2start)




