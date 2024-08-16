# -*- coding: UTF-8 -*-

from aiogram.types import Message
from aiogram import Router

router = Router()

@router.edited_message()
async def edited_message_allert(message: Message) -> None:
    await message.answer("Редактировать сообщения нельзя. Если у вас есть исправления вашего прошлого сообщения - исправьте его и отправьте в бот еще раз.")
    