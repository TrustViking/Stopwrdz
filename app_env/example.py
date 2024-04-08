




    def replace_swords_buffer_bytes(self, 
                             buf: BytesIO, 
                             diction: Dict[str, str], 
                             punctuation: List[str]) -> Optional[BytesIO]:
        """
        Заменяет стоп-слова в буфере формата BytesIO согласно словарю.

        Args:
            self: Экземпляр класса.
            buf (BytesIO): Буфер с данными для замены слов.
            diction (Dict[str, str]): Словарь, где ключи - слова для замены, 
                                      а значения - заменяющие слова.
            punctuation (List[str]): Список знаков пунктуации.

        Returns:
            Optional[BytesIO]: Буфер с замененными словами или None в случае ошибки.
        """
        @safe_execute(logger=self.logger, name_method=f'[{__name__}|{self.cls_name}]')
        def _replace_swords_buffer_bytes():
            # создаем новый буфер
            new_buf = BytesIO()
            
            # позиция курсора в начало буфера
            buf.seek(0)

            # Проходим по каждой строке в буфере
            for line in buf.readlines():
                decoded_line = line.decode('utf-8')
                # Разбираем строку на слова, заменяем стоп-слова и восстанавливаем пунктуацию                
                string_after_replace = self.string_disassembled(decoded_line, diction, punctuation)
                if string_after_replace is None: 
                    msg = (
                            f'\n*ERROR [{__name__}|{self.cls_name}]'
                            f'\n*Не смогли обработать строку на предмет замены стоп-слов'
                            f'\n*string_after_replace: [{string_after_replace}]'
                            )
                    print(msg)
                    self.logger.log_info(msg) 
                    return None 
                
                # Кодируем строку обратно в бинарный формат
                new_line = string_after_replace.encode('utf-8')
                # Записываем строку в новый буфер
                new_buf.write(new_line + b'\n')

            return new_buf
        return _replace_swords_buffer_bytes()
