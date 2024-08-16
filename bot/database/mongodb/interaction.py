# -*- coding: UTF-8 -*-

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import Union
import logging


from helper_classes.assistant import MinorOperations

helper = MinorOperations()

        
class Interaction:
	def __init__(self) -> None:
		"""
        Подключение к базе для локального развертывания проекта
        """
		#mongo_client = AsyncIOMotorClient(f'mongodb://localhost:27017')
		"""
        Подключение к базе для развертывания проекта на сервере
        """
		mongo_client = AsyncIOMotorClient(f'mongodb://{helper.get_mongo_login()}:{helper.get_mongo_password()}@mongodb:27017')
		self.__db = mongo_client['hub_bot']
		self.__current_data = self.__db['general_info_about_user'] #Коллекция с данными о пользователях


	async def init_user(self, user_id: int, user_addr: str, user_name: str) -> str:
		"""
		Инициализация пользователя в базе данных
		"""
		document = await self.find_data({"_id": ObjectId("66bf2af6825485184a414d78")})
  
		quantity_users = len(document['users'])

		user_log = 0

		for users in range(quantity_users):
			is_user_log_in= document['users'][users]['tg_id']
			if is_user_log_in == user_id:# Поиск ячейки хранения данных для пользователя
				user_log = 1
				return document['users'][users]['id_topic_chat']

		if not(user_log):
			new_user = {
				'tg_id': user_id,
				'tg_addr': f'@{user_addr}',
				'full_name': user_name,
    			'id_topic_chat': ''
		}
			update = {'$push': {'users': new_user}}
			await self.update_data(document, update)

			logging.warning(f"Added new user: {user_id} Total number of users: {quantity_users}")
			return None
	
 
	async def find_data(self, filter: dict) -> dict:
		"""
    	Точка входа в таблицу с данными о пользователях
    	"""
		return await self.__current_data.find_one(filter)

	
	async def update_data(self, filter: dict, update: int) -> None:
		"""
    	Обновление данных в ячейке БД
    	"""
		await self.__current_data.update_one(filter, update)

	
	async def get_data(self, user_id: int, type_data: str) -> Union[int, str, float, dict]:
		"""
    	Получение данных из ячейки БД
    	"""
		filter_by_id = {'tg_id': user_id}
		result = await self.__current_data.find_one({'users': {'$elemMatch': filter_by_id}},{'users.$': 1})

		return result['users'][0][f'{type_data}']


	async def get_users_id_and_tg_adreses(self) -> dict:
		"""
		Получение массива id пользователей для отправки рассылки
  		"""
		document = await self.find_data({"_id": ObjectId("66bf2af6825485184a414d78")})
		quantity_users = len(document['users'])
		users_data = []
		for users in range(quantity_users):
			user_id = document['users'][users]['tg_id']
			tg_addr = document['users'][users]['tg_addr']
			users_data.append([str(user_id),tg_addr])
		
		return users_data


	async def find_user_id(self, message_thread_id: int) -> str:
		"""
		Инициализация пользователя в базе данных
		"""
		document = await self.find_data({"_id": ObjectId("66bf2af6825485184a414d78")})
  
		quantity_users = len(document['users'])

		user_log = 0

		for users in range(quantity_users):
			user_topic_id = document['users'][users]['id_topic_chat']
			if user_topic_id == message_thread_id:# Поиск ячейки хранения данных для пользователя
				return document['users'][users]['tg_id']