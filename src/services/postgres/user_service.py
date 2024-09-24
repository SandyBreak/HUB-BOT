# -*- coding: UTF-8 -*-

from datetime import datetime
from typing import Optional
import logging

from sqlalchemy import select, func, update
from sqlalchemy.exc import SQLAlchemyError

from models.table_models.user import User

from services.postgres.database import get_async_session

#from exceptions.errors import UserNotRegError, RegistrationError


class UserService:
    def __init__(self):
        pass
    
    
    @staticmethod
    async def init_user(user_id: int, nickname: str, full_name: str) -> None:
        """
        Регистрация пользователя, сохранение:
            1. ID Аккаунта
            2. Адрес аккаунта
            3. Имя аккаунта
            5. Даты регистрации
        """
        async for session in get_async_session():
            try:
                user_exists_query = await session.execute(
                    select(func.count('*'))
                    .where(User.id_tg == user_id)
                )
                user_exists_flag = user_exists_query.scalar()
                
                if not user_exists_flag:
                    new_user = User(
                        id_tg=user_id,
                        nickname=nickname,
                        fullname=full_name,
                        date_reg=datetime.now(),
                    )

                    # Выполнение вставки
                    session.add(new_user)
                    await session.commit()
                
            except SQLAlchemyError as e:
                logging.error(f"Ошибка первичной регистрации пользователя: {e}")