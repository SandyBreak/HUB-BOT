# -*- coding: UTF-8 -*-

import logging

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router, Bot

from services.postgres.group_service import GroupService
from services.postgres.user_service import UserService

from models.long_messages import HELP_MESSAGE


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message, bot: Bot) -> None:
    SUPER_GROUP_ID = await GroupService.get_group_id()
    if not(SUPER_GROUP_ID):
        logging.critical('Bot doesn''t activated')
        return
    
    hello_message = f'''Здравствуйте!

Напишите ваш вопрос и мы ответим Вам в ближайшее время.
    '''
    await UserService.init_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    id_topic_chat = await GroupService.get_user_message_thread_id(message.from_user.id)
    
    if not(id_topic_chat):
        try:
            new_topic = await bot.create_forum_topic(chat_id=SUPER_GROUP_ID, name=message.from_user.full_name)
            await GroupService.save_user_message_thread_id(message.from_user.id, new_topic.message_thread_id)
        except Exception as e:
            logging.error(f'Error create forum topic: {e}')
        
        new_user_message = await bot.send_message(chat_id=SUPER_GROUP_ID, text=f'ID пользователя: {message.from_user.id}\nИмя пользователя: {message.from_user.full_name}\nАдрес пользователя: @{message.from_user.username}', reply_to_message_id=new_topic.message_thread_id)
        await bot.pin_chat_message(chat_id=SUPER_GROUP_ID, message_id=new_user_message.message_id)
        
        await message.answer(hello_message)
    else:
        await message.answer(hello_message)
        
          
@router.message(Command('help'))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_MESSAGE)