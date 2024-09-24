# -*- coding: UTF-8 -*-

import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram import Router, F, Bot
from aiogram.types import Message
from contextlib import suppress

from admin.admin_keyboards import AdminKeyboards

from services.postgres.group_service import GroupService
from services.postgres.user_service import UserService

router = Router()

    
@router.message(F.document)
@router.message(F.voice)
@router.message(F.photo)
@router.message(F.video)
@router.message(F.text.not_in(['/start', '/control', '/help', '/init']))
async def catch_message(message: Message, bot: Bot) -> None:
    bot_data = await bot.get_me()

    SUPER_GROUP_ID = await GroupService.get_group_id()
    if not(SUPER_GROUP_ID):
        logging.critical('Bot doesn''t activated')
        return
    with suppress(AttributeError):
        left_member_id = message.left_chat_participant.get('id')
        if left_member_id == bot_data.id:
            logging.info('Ignore kik bot exception message')
            return
    with suppress(AttributeError):
        new_member_id = message.new_chat_member.get('id')
        if new_member_id == bot_data.id:
            logging.info('Ignore hello message from added bot')
            return
    '''
    Защита от того чтобы данные бота не попали в базу
    '''
    if message.from_user.id != bot_data.id:
        await UserService.init_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
        id_topic_chat = await GroupService.get_user_message_thread_id(message.from_user.id)
    else: 
        return
    
    '''
    Если у пользователя нету id темы с его именем
    '''
    if not(id_topic_chat):
        try:
            '''
            Создаем новую тему
            '''
            new_topic = await bot.create_forum_topic(chat_id=SUPER_GROUP_ID, name=message.from_user.full_name)
            await GroupService.save_user_message_thread_id(message.from_user.id, new_topic.message_thread_id)
        except TelegramBadRequest as e:
            if 'not enough rights' in str(e):
                    logging.error(f'Not enough rights!')
                    await bot.send_message(chat_id=SUPER_GROUP_ID, text=f'Обнаружен новый пользователь!\n\nЯ не могу создать новый диалог с ним из-за того у моих прав недостаточно!\n\nНазначьте меня администратором!')
                    return
        except Exception as e:
            logging.error(f'Error create forum topic: {e}')
        '''
        Отправляем сообщение с информацией о пользователе и закрепляем его
        '''
        new_user_message = await bot.send_message(chat_id=SUPER_GROUP_ID, text=f'ID пользователя: {message.from_user.id}\nИмя пользователя: {message.from_user.full_name}\nАдрес пользователя: @{message.from_user.username}', reply_to_message_id=new_topic.message_thread_id)
        await bot.pin_chat_message(chat_id=SUPER_GROUP_ID, message_id=new_user_message.message_id)
        await bot.copy_message(chat_id=SUPER_GROUP_ID, from_chat_id=message.chat.id, message_id=message.message_id, message_thread_id=new_topic.message_thread_id, protect_content=None)
    elif id_topic_chat:
        '''
        Если сообщение написано не в группе и у пользователя есть номер его темы
        '''
        if (message.chat.id != SUPER_GROUP_ID):
            try:
                '''
                Изменяем имя темы если у пользователя изменились имя и фамилия и обновляем сообщение с информацией о пользователе
                '''
                with suppress(TelegramBadRequest):
                    try:
                        await bot.edit_forum_topic(chat_id=SUPER_GROUP_ID, message_thread_id=id_topic_chat, name=message.from_user.full_name)
                        new_user_message = await bot.send_message(chat_id=SUPER_GROUP_ID, text=f'ID пользователя: {message.from_user.id}\nИмя пользователя: {message.from_user.full_name}\nАдрес пользователя: @{message.from_user.username}', reply_to_message_id=id_topic_chat)
                        await bot.pin_chat_message(chat_id=SUPER_GROUP_ID, message_id=new_user_message.message_id)
                    except TelegramBadRequest as e:
                        if 'not enough rights' in str(e):
                                logging.error(f'Not enough rights!')
                                await bot.send_message(chat_id=SUPER_GROUP_ID, text='Назначьте меня администратором!')
                
                await bot.copy_message(chat_id=SUPER_GROUP_ID, from_chat_id=message.chat.id, message_id=message.message_id, message_thread_id=id_topic_chat, protect_content=None)
            
            except TelegramBadRequest as e:
                '''
                Если тема была удалена
                '''
                if 'message thread not found' in str(e):
                    logging.error(f'Message thread not found re-creating the topic...')
                    try:
                        '''
                        Создаем новую тему
                        '''
                        new_topic = await bot.create_forum_topic(chat_id=SUPER_GROUP_ID, name=message.from_user.full_name)
                        await GroupService.save_user_message_thread_id(message.from_user.id, new_topic.message_thread_id)
                    except TelegramBadRequest as e:
                        if 'not enough rights' in str(e):
                                logging.error(f'Not enough rights!')
                                await bot.send_message(chat_id=SUPER_GROUP_ID, text='Назначьте меня администратором!')
                                return
                    except Exception as e:
                        logging.error(f'Error create forum topic: {e}')
                        
                    '''
                    Отправляем сообщение с информацией о пользователе и закрепляем его
                    '''
                    new_user_message = await bot.send_message(chat_id=SUPER_GROUP_ID, text=f'ID пользователя: {message.from_user.id}\nИмя пользователя: {message.from_user.full_name}\nАдрес пользователя: @{message.from_user.username}', reply_to_message_id=new_topic.message_thread_id)
                    await bot.pin_chat_message(chat_id=SUPER_GROUP_ID, message_id=new_user_message.message_id)
                    await bot.copy_message(chat_id=SUPER_GROUP_ID, from_chat_id=message.chat.id, message_id=message.message_id, message_thread_id=new_topic.message_thread_id, protect_content=None)
                else:
                    logging.error(f'Unknown error: {e}')
        elif message.is_topic_message and message.from_user.id != bot_data.id:
            '''
            Если сообщение написано в одной из тем и это сообщение принадлежит не боту
            '''
            message_thread_id = message.message_thread_id
            logging.critical(message_thread_id)
            user_chat_id = await GroupService.get_user_id(message_thread_id)
            '''
            Отправляем сообщение пользователю, которому принадлежит тема 
            '''
            await bot.copy_message(chat_id=user_chat_id, from_chat_id=message.chat.id, message_id=message.message_id, protect_content=None)
        
        elif not message.is_topic_message:
            '''
            Если сообщение написано в главной теме, Дублируем сообщение с клавитурой управления рассылкой
            '''
            keyboard = await AdminKeyboards.newsletter_keyboard()
            edit_message = await bot.copy_message(chat_id=SUPER_GROUP_ID, from_chat_id=message.chat.id, message_id=message.message_id, protect_content=None)
            await bot.delete_message(chat_id=SUPER_GROUP_ID, message_id=message.message_id,)
            await bot.edit_message_reply_markup(chat_id=SUPER_GROUP_ID, message_id=edit_message.message_id, reply_markup=keyboard.as_markup())