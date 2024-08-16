# -*- coding: UTF-8 -*-

from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram import Router, Bot, F
import logging


from admin.config import LIST_USERS_TO_NEWSLETTER, SUPER_GROUP_ID
from admin.assistant import AdminOperations
from admin.keyboards import AdminKeyboards


from database.mongodb.interaction import Interaction

from data_storage.emojis import Emojis

mongodb_interface = Interaction()
bank_of_keys = AdminKeyboards()
helper = AdminOperations()
router = Router()
emojis = Emojis()

    
@router.message(Command('control'))
async def get_pass(message: Message, state: FSMContext, bot: Bot):
    root_keyboard = await bank_of_keys.possibilities_keyboard()     
    if (message.chat.id == SUPER_GROUP_ID) and not(message.message_thread_id):
        await message.answer(f"Выберите одно из нижеперечисленных действий", reply_markup=root_keyboard.as_markup())


@router.callback_query(F.data)
async def choose_action(callback: CallbackQuery, state: FSMContext, bot: Bot):
    action, user_id, user_tg_addr = await helper.parse_callback_data(callback.data)
    if action == 'manual':
        await get_manual_admin_panel(callback)
        await callback.answer()
    if action == 'menu':
        root_keyboard = await bank_of_keys.possibilities_keyboard()
        await callback.message.answer(f"{emojis.ARROW_DOWN} Выберите одно из нижеперечисленных действий {emojis.ARROW_DOWN}", reply_markup=root_keyboard.as_markup())
        await callback.answer()
    elif action == 'global_newsletter':
        await global_newsletter(callback, bot)
        await callback.answer()
    elif action == 'targeted_newsletter':
        list_users = await bank_of_keys.keyboard_for_adding_users_in_targeted_newsletter(None)
        await bot.edit_message_reply_markup(chat_id=SUPER_GROUP_ID, message_id=callback.message.message_id, reply_markup=list_users.as_markup())
        await callback.answer()    
    elif action == 'cancel_newsletter':
        await cancel_newsletter(callback, bot)
    elif action == 'accept_newsletter':
        await targeted_newsletter(callback, bot)
        await callback.answer() 
    elif action == 'view_active_users':
        await view_active_users(callback, bot)
    elif action == 'ADD':
        await add_user_to_newsletter(callback, user_id, user_tg_addr)
        update_list_users = await bank_of_keys.keyboard_for_adding_users_in_targeted_newsletter(LIST_USERS_TO_NEWSLETTER)
        await bot.edit_message_reply_markup(chat_id=SUPER_GROUP_ID, message_id=callback.message.message_id, reply_markup=update_list_users.as_markup())



async def get_manual_admin_panel(callback: CallbackQuery):
    manual_message = """
<b>Как делать рассылки:</b> Отправляем в чат Admin Panel любое сообщение и выбилоролрраем что с ним сделать.
1. <b>Запустить глобальную рассылку:</b> Отправить сообщение всем пользователям
2. <b>Запустить точечную рассылку:</b> Отправить сообщение выбранным пользователям
3. <b>Удалить сообщение:</b> Удалить сообщение и отменить рассылку

<b>Посмотреть список активных/не активных пользователей:</b>
Получить список активных пользователей
    """
    await callback.message.answer(manual_message, ParseMode.HTML)
    await callback.answer()

async def cancel_newsletter(callback: CallbackQuery, bot: Bot) -> None:
    if (callback.message.chat.id == SUPER_GROUP_ID) and not(callback.message.message_thread_id):
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        
        
async def global_newsletter(callback: CallbackQuery, bot: Bot) -> None:
    """
    Глобальная рассылка обновлений
    """
    if (callback.message.chat.id == SUPER_GROUP_ID) and not(callback.message.message_thread_id):
        user_data = await mongodb_interface.get_users_id_and_tg_adreses()
        try:
            received_users = []
            not_received_users =[]
            for user in user_data:
                user_id = user[0]
                user_tg_addr = user[1]
                try:
                    await bot.copy_message(chat_id=user_id, from_chat_id=callback.message.chat.id, message_id=callback.message.message_id, protect_content=None)
                    received_users.append([user_id, user_tg_addr])
                except Exception as e:
                    if "chat not found" in str(e):
                        logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                        not_received_users.append([user_id, user_tg_addr, 'Чат не найден'])
                    elif "bot was blocked" in str(e):
                        logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                        not_received_users.append([user_id, user_tg_addr, 'Заблокировал бота'])
                    else:
                        logging.warning(f"Skipping user_id {user_id} unknown error {e}")
                        not_received_users.append([user_id, user_tg_addr, f'Другая ошибка{e}'])
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
            if received_users:
                message_report = 'Получившие пользователи:\n'

                for user in received_users:
                    user_id=user[0]
                    user_tg_addr=user[1]
                    message_report += f'ID: {user_id} Адрес: {user_tg_addr}\n'

            if not_received_users:
                message_report += 'Не получившие пользователи:\n'
                
                for user in not_received_users:
                    user_id = user[0]
                    user_tg_addr = user[1]
                    reason = user[2]
                    message_report += f'ID: {user_id} Адрес: {user_tg_addr} Причина: {reason}\n'  

            await callback.message.answer(f'{emojis.SUCCESS} Рассылка завершена успешно!')
            await callback.message.answer(f'{message_report}')
        except Exception as e:
            logging.error(f"Error during global_newsletter: {e}")


async def targeted_newsletter(callback: CallbackQuery, bot: Bot) -> None:
    """
    Точечная рассылка обновлений
    """
    if (callback.message.chat.id == SUPER_GROUP_ID) and not(callback.message.message_thread_id):
        user_data = LIST_USERS_TO_NEWSLETTER
        if user_data:
            try:
                received_users = []
                not_received_users =[]
                for user in user_data:
                    user_id = user[0]
                    user_tg_addr = user[1]
                    try:
                        await bot.copy_message(chat_id=user_id, from_chat_id=callback.message.chat.id, message_id=callback.message.message_id, protect_content=None)
                        received_users.append([user_id, user_tg_addr])
                    except Exception as e:
                        if "chat not found" in str(e):
                            logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                            not_received_users.append([user_id, user_tg_addr, 'Чат не найден'])
                        elif "bot was blocked" in str(e):
                            logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                            not_received_users.append([user_id, user_tg_addr, 'Заблокировал бота'])
                        else:
                            logging.warning(f"Skipping user_id {user_id} unknown error{e}")
                            not_received_users.append([user_id, user_tg_addr, f'Другая ошибка{e}'])
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
                message_report = 'Получившие пользователи:\n'
                if received_users:
                    for user in received_users:
                        user_id=user[0]
                        user_tg_addr=user[1]
                        message_report += f'ID: {user_id} Адрес: {user_tg_addr}\n'

                message_report += 'Не получившие пользователи:\n'
                if not_received_users:
                    for user in not_received_users:
                        user_id = user[0]
                        user_tg_addr = user[1]
                        reason = user[2]
                        message_report += f'ID: {user_id} Адрес: {user_tg_addr} Причина: {reason}\n' 
                LIST_USERS_TO_NEWSLETTER.clear()
                await callback.message.answer(f'{emojis.SUCCESS} Рассылка завершена успешно!')
                await callback.message.answer(f'{message_report}')
            except Exception as e:
                logging.error(f"Error during targeted_newsletter: {e}")
        else:
            await callback.message.answer(f'{emojis.ALLERT} Вы не добавили в рассылку ни одного пользователя')

async def view_active_users(callback: CallbackQuery, bot: Bot) -> None:
    user_data = await mongodb_interface.get_users_id_and_tg_adreses()
    
    active_users = []
    not_active_users = []
    other_users = []
    
    users_list_str = 'Список пользователей:\n'
    
    for user in user_data:
        user_id = user[0]
        user_tg_addr = user[1]
        try:
            chat = await bot.get_chat(chat_id=user_id)
            if chat:
                active_users.append([user_id, user_tg_addr])
        except Exception as e:
                if "chat not found" in str(e):
                    logging.warning(f"Skipping user_id {user_id} due to 'chat not found' error")
                    not_active_users.append([user_id, user_tg_addr,])
                else:
                    logging.warning(f"Skipping user_id {user_id} unknown error{e}")
                    other_users.append([user_id, user_tg_addr, e])
    
    if active_users:
        users_list_str += '\nСтатус АКТИВЕН:\n'
        for user in active_users:
            user_id=user[0]
            user_tg_addr=user[1]
            users_list_str += f'ID: {user_id} Адрес: {user_tg_addr}\n'
    
    if not_active_users:
        users_list_str += '\nСтатус НЕ АКТИВЕН:\n'
        for user in not_active_users:
            user_id=user[0]
            user_tg_addr=user[1]
            users_list_str += f'ID: {user_id} Адрес: {user_tg_addr}\n'
    
    if other_users:
        users_list_str += '\nСтатус ДРУГАЯ ОШИБКА:\n'
        for user in other_users:
            user_id=user[0]
            user_tg_addr=user[1]
            error = user[2]
            users_list_str += f'ID: {user_id} Адрес: {user_tg_addr} Ошибка: {error}\n'
            
    await callback.message.answer(users_list_str)
    await callback.answer()


async def add_user_to_newsletter(callback: CallbackQuery, user_id: str, user_tg_addr: str):
    if [user_list for user_list in LIST_USERS_TO_NEWSLETTER if user_id in user_list]:
        LIST_USERS_TO_NEWSLETTER.pop()
        await callback.answer()    
    else:
        LIST_USERS_TO_NEWSLETTER.append([user_id, user_tg_addr])
        await callback.answer()
