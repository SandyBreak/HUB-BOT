# -*- coding: UTF-8 -*-

from typing import Optional
import logging

from sqlalchemy import delete, select, update

from services.postgres.database import get_async_session

from models.table_models.admin_group import AdminGroup
from models.table_models.user import User


class GroupService:
    def __init__(self):
        pass

    @staticmethod
    async def group_init(id_group: int) -> None:
        """
        Идентификация в группе
        """
        try:
            async for session in get_async_session():
                session.add(AdminGroup(group_id=id_group))
                await session.commit()
        except Exception as e:  # Ловим все исключения
            logging.error(f"Ошибка при идентификации группы: {e}")
    
    
    @staticmethod
    async def group_reset() -> None:
        """
        Сброс группы
        """
        try:
            async for session in get_async_session():
                await session.execute(delete(AdminGroup))
                
                await session.commit()  # Подтверждаем изменения
        except Exception as e:
            await session.rollback()  # Откатываем изменения в случае ошибки
            logging.error(f"Ошибка при сбросе группы: {e}")
    
    
    @staticmethod
    async def get_group_id() -> Optional[str]:
        """
        Получение ID группы
        """
        try:
            async for session in get_async_session():
                get_group_id = await session.execute(select(AdminGroup.group_id))
                id_group = get_group_id.scalar()
                if id_group:
                    return id_group
                else:
                    return None
        except Exception as e:
            logging.error(f"Ошибка при получении ID группы: {e}")
            
            
    @staticmethod
    async def get_user_message_thread_id(user_tg_id: int) -> bool:
        """
        Получает id чата с пользователем для группы.
        """
        try:
            async for session in get_async_session():
                get_user_message_thread_id = await session.execute(select(User.id_topic_chat)
                    .select_from(User)
                    .where(User.id_tg == user_tg_id)
                )
                message_thread_id = get_user_message_thread_id.scalar()
                return message_thread_id
        except Exception as e:
            logging.error(f"Ошибка при получении id чата пользователя в группе: {e}")

    
    @staticmethod
    async def save_user_message_thread_id(user_tg_id: int, message_thread_id: int) -> bool:
        """
        Получает id чата с пользователем для группы.
        """
        try:
            async for session in get_async_session():
                await session.execute(
                        update(User)
                        .where(User.id_tg==user_tg_id)
                        .values(
                            id_topic_chat=message_thread_id)
                        )
                await session.commit()
        except Exception as e:
            logging.error(f"Ошибка при получении id чата пользователя в группе: {e}")
            
    
    @staticmethod
    async def get_user_id(message_thread_id: int) -> bool:
        """
        Ищет id пользователя для переданного message_thread_id
        """
        try:
            async for session in get_async_session():
                get_user_id_query = await session.execute(select(User.id_tg)
                    .select_from(User)
                    .where(User.id_topic_chat == message_thread_id)
                )
                user_id_tg = get_user_id_query.scalar()
                return user_id_tg
        except Exception as e:
            logging.error(f"Ошибка при получении id пользователя по id чата группы: {e}")
    