# -*- coding: UTF-8 -*-

import os


class MinorOperations:
    def __init__(self) -> None:
        self.auth_client = None

    
    async def get_tg_token(self) -> str:
        """
        Получение токена бота
        """
        return os.environ.get('TELEGRAM_TOKEN')    
    
   
    def get_mongo_login(self) -> str:
        """
        Получение логина пользователя базы данных
        """
        return os.environ.get('MONGO_INITDB_ROOT_USERNAME')
    
    
    def get_mongo_password(self) -> str:
        """
        Получение пароля пользователя базы данных
        """
        return os.environ.get('MONGO_INITDB_ROOT_PASSWORD')