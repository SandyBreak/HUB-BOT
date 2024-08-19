# -*- coding: UTF-8 -*-

from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router, Bot
import logging

from database.mongodb.interaction import Interaction


mongodb_interface = Interaction()
router = Router()
from admin.assistant import AdminOperations

helper = AdminOperations()

@router.message(Command('start'))
async def cmd_start(message: Message, bot: Bot) -> None:
    SUPER_GROUP_ID = await mongodb_interface.get_super_group_id()
    if not(SUPER_GROUP_ID):
        logging.critical('Bot doesn''t activated')
        return
    
    hello_message = f'''Здравствуйте!

Напишите ваш вопрос и мы ответим Вам в ближайшее время.
    '''
    id_topic_chat = await mongodb_interface.init_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    if not(id_topic_chat):
        try:
            new_topic = await bot.create_forum_topic(chat_id=SUPER_GROUP_ID, name=message.from_user.full_name)
            filter_by_id = {'users.tg_id': message.from_user.id}
            update = {'$set': {f'users.$.id_topic_chat': new_topic.message_thread_id}}
            await mongodb_interface.update_data(filter_by_id, update)
        except Exception as e:
            logging.error(f'Error create forum topic: {e}')
        
        new_user_message = await bot.send_message(chat_id=SUPER_GROUP_ID, text=f'ID пользователя: {message.from_user.id}\nИмя пользователя: {message.from_user.full_name}\nАдрес пользователя: @{message.from_user.username}', reply_to_message_id=new_topic.message_thread_id)
        await bot.pin_chat_message(chat_id=SUPER_GROUP_ID, message_id=new_user_message.message_id)
        
        await message.answer(hello_message)
    else:
        await message.answer(hello_message)
        
        
        
@router.message(Command('help'))
async def cmd_help(message: Message, bot: Bot) -> None:
    help_message = f'''Возможности бота:
1. Вы можете отправлять в бот текст, фото, видео, документы, а так же голосовые сообщения

2. Вы можете пересылать боту чужие сообщения, но получателю вашего сообщения не будет видно имени человека, чьи сообщения были пересланы

3. Вы не можете редактировать сообщения. Если у вас есть исправления вашего прошлого сообщения - исправьте его и отправьте в бот еще раз.

4. Если по какой то причине вы не получаете ответ в течении долгого времени (2 и более дней), можете обратиться к администратору бота по адресу @velikiy_ss
    '''
    await message.answer(help_message)