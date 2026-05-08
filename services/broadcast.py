from typing import List
from pyrogram import Client
from database.crud import crud
from services.post_service import post_service
from utils.logger import logger

class BroadcastService:
    @staticmethod
    async def broadcast_to_channels(
        client: Client,
        content_type: str,
        file_id: str = None,
        caption: str = None
    ):
        channels = await crud.get_channels()
        results = {"success": 0, "failed": 0}
        
        for ch in channels:
            try:
                await post_service.send_to_channel(
                    client,
                    ch["channel_id"],
                    content_type,
                    file_id,
                    caption
                )
                results["success"] += 1
            except Exception as e:
                logger.error(f"Broadcast failed for {ch['title']}: {e}")
                results["failed"] += 1
                
        return results

broadcast_service = BroadcastService()
