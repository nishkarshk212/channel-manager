from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from utils.logger import logger

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            self.db = self.client.get_default_database()
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

db = MongoDB()
