from pyrogram import Client, types
from typing import List, Optional
from database.crud import crud
from utils.logger import logger

class PostService:
    @staticmethod
    async def send_to_channel(
        client: Client,
        channel_id: int,
        content_type: str,
        file_id: Optional[str] = None,
        caption: Optional[str] = None,
        reply_markup: Optional[types.InlineKeyboardMarkup] = None,
        entities: Optional[List[types.MessageEntity]] = None
    ):
        try:
            if content_type == "text":
                return await client.send_message(channel_id, caption, reply_markup=reply_markup, entities=entities)
            elif content_type == "photo":
                return await client.send_photo(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities)
            elif content_type == "video":
                return await client.send_video(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities)
            elif content_type == "document":
                return await client.send_document(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities)
            elif content_type == "audio":
                return await client.send_audio(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities)
        except Exception as e:
            logger.error(f"Error sending post to {channel_id}: {e}")
            raise

post_service = PostService()
