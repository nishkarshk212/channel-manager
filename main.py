from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from config import settings
from database.connection import db
from database.crud import crud
from database.models import User
from utils.logger import logger
import asyncio

from handlers.scheduler import Scheduler

class ChannelBot(Client):
    def __init__(self):
        super().__init__(
            "channel_manager_bot",
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            bot_token=settings.BOT_TOKEN,
            plugins=dict(root="handlers"),
            workers=20
        )
        self.scheduler = None

    async def start(self, *args, **kwargs):
        logger.info("Bot is starting...")
        try:
            if settings.USE_MONGODB:
                await db.connect()
            else:
                logger.info("Using Local JSON Database")
            
            await super().start(*args, **kwargs)
            logger.info("Pyrogram Client started.")
            
            # Start Scheduler
            self.scheduler = Scheduler(self)
            self.scheduler.start()
            logger.info("Scheduler started.")
            
            # Ensure owner is registered
            owner = await crud.get_user(settings.OWNER_ID)
            if not owner:
                await crud.create_user(User(
                    user_id=settings.OWNER_ID,
                    role="owner"
                ))
            
            logger.info("Bot initialization complete. Running...")
        except Exception as e:
            logger.error(f"CRITICAL ERROR DURING STARTUP: {e}", exc_info=True)
            raise

    async def stop(self, *args):
        await super().stop()
        await db.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    bot = ChannelBot()
    bot.run()
