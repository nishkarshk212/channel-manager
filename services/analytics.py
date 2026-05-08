from pyrogram import Client, filters
from database.crud import crud
from utils.logger import logger
from datetime import datetime, timedelta

class AnalyticsService:
    @staticmethod
    async def track_view(channel_id: int, message_id: int):
        # In a real app, you'd store this in MongoDB
        # For now, we'll just log it
        pass

    @staticmethod
    async def get_channel_stats(client: Client, channel_id: int):
        try:
            chat = await client.get_chat(channel_id)
            members = chat.members_count
            return {
                "title": chat.title,
                "members": members,
                "username": chat.username
            }
        except Exception as e:
            logger.error(f"Error getting stats for {channel_id}: {e}")
            return None

analytics_service = AnalyticsService()
