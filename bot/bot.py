#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from aiogram.types.bot_command import BotCommand
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
import logging


from admin import admin_panel
from routers import main_router, actions, commands


from helper_classes.assistant import MinorOperations
from database.mongodb.mongo_init import create_db
from data_storage.emojis import Emojis


helper = MinorOperations()
emojis = Emojis()


async def set_commands_and_description(bot: Bot) -> None:
    commands = [
    BotCommand(
        command='/start',
        description='Перезапустить бота'
		),
    BotCommand(
        command='/help',
        description='Помощь'
		)
    ]
    long_description_one = f'''Напишите ваш вопрос и мы ответим Вам в ближайшее время.'''
    short_description = f''
    
    await bot.set_my_description(description=long_description_one)
    await bot.set_my_short_description(short_description=short_description)
    await bot.set_my_commands(commands)
    
async def main():
    load_dotenv()#Потом убрать надо
    
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m %H:%M')
    
    bot = Bot(token=await helper.get_tg_token())
    dp = Dispatcher()
    
    await set_commands_and_description(bot)
    dp.include_router(main_router.router)
    dp.include_router(commands.router)
    dp.include_router(actions.router)
    dp.include_router(admin_panel.router)
    

    await create_db()
    await dp.start_polling(bot)
    logging.warning('BOT STARTED')
    

if __name__ == '__main__':
    asyncio.run(main())
    