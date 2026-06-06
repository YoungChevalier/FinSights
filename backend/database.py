from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_manager = Database()

async def get_database():
    if db_manager.client is None:
        db_manager.client = AsyncIOMotorClient(settings.mongo_uri)
        db_manager.db = db_manager.client[settings.database_name]
    return db_manager.db

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        db_manager.client = None
