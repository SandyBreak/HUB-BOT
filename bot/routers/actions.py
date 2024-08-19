# -*- coding: UTF-8 -*-

from aiogram.types import Message
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram import Router, Bot
import logging
router = Router()

@router.edited_message()
async def edited_message_allert(message: Message) -> None:
    await message.answer('Редактировать сообщения нельзя. Если у вас есть исправления вашего прошлого сообщения - исправьте его и отправьте в бот еще раз.')
    
    
@router.my_chat_member()
async def my_chat_member_handler(message: Message, bot: Bot):
    if message.new_chat_member.status == ChatMemberStatus.MEMBER:
        member = message.new_chat_member
        if member.user.id == bot.id and message.from_user.id == 5890864355:  # Проверяем, добавлен ли бот
            await message.answer('Спасибо за добавление меня в группу! Для моей правильной работы назначьте меня администратором')
            logging.warning(f'Bot was added in group! ID: {message.chat.id}, adder_ID: {message.from_user.id}, adder_addr: {message.from_user.username}')
        elif message.from_user.id != 5890864355:
            await message.answer('У вас нету прав чтобы добавлять меня в эту группу, до свидания!')
            await bot.leave_chat(message.chat.id)
    elif message.new_chat_member.status == ChatMemberStatus.LEFT:
        logging.critical(f'Bot was kikked from group! ID: {message.chat.id}, adder_ID: {message.from_user.id}, adder_addr: {message.from_user.username}')
    elif message.new_chat_member.status == ChatMemberStatus.ADMINISTRATOR:
        await message.answer('Теперь я администратор!')
    elif message.new_chat_member.status != ChatMemberStatus.ADMINISTRATOR:
        await message.answer('Я больше не администратор!')
           