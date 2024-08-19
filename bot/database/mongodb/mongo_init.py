from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging

from helper_classes.assistant import MinorOperations

helper = MinorOperations()


async def create_db():
    try:
        '''
        Подключение к базе для локального развертывания проекта
        '''
        #new_db = AsyncIOMotorClient(f'mongodb://localhost:27017')    
        '''
        Подключение к базе для развертывания проекта на сервере
        '''
        new_db = AsyncIOMotorClient(f'mongodb://{helper.get_mongo_login()}:{helper.get_mongo_password()}@mongodb:27017')
            
        new_table = new_db['hub_bot']
        general_info_about_user = new_table['general_info_about_user'] #Коллекция с данными о пользователях
        
        users = {'_id': ObjectId('66bf2af6825485184a414d78'),'super_group_id': None, 'users': []}
        
        await general_info_about_user.insert_one(users)
        
    except Exception as e:
        logging.error(f'Error during create DataBase: {e}')