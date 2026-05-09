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
            # Ensure channel_id is an integer if it looks like one
            if isinstance(channel_id, str):
                try:
                    if channel_id.startswith("-100") or channel_id.startswith("-"):
                        channel_id = int(channel_id)
                except ValueError:
                    pass

            # Try to resolve peer if it's a numeric ID and might not be in cache
            try:
                await client.get_chat(channel_id)
            except Exception as e:
                logger.warning(f"Could not pre-resolve chat {channel_id} by ID: {e}")
                # Try resolving via username from DB if ID fails
                channel_data = await crud.get_channel_by_id(channel_id) if isinstance(channel_id, int) else None
                if channel_data and channel_data.get("username"):
                    username = channel_data["username"]
                    logger.info(f"Attempting to resolve chat via username: @{username}")
                    try:
                        chat = await client.get_chat(username)
                        channel_id = chat.id  # Update ID to the resolved one
                    except Exception as e2:
                        logger.error(f"Failed to resolve chat via username @{username}: {e2}")

            # Convert dict entities back to MessageEntity if necessary
            if entities and isinstance(entities, list) and isinstance(entities[0], dict):
                from pyrogram.types import MessageEntity
                from pyrogram.enums import MessageEntityType
                
                reconstructed_entities = []
                for e in entities:
                    # Map string type back to Enum if possible
                    entity_type = e.get("type")
                    if isinstance(entity_type, str):
                        try:
                            entity_type = getattr(MessageEntityType, entity_type.upper())
                        except AttributeError:
                            pass
                    
                    # Ensure custom_emoji_id is an integer (fixes 'to_bytes' error)
                    emoji_id = e.get("custom_emoji_id")
                    if emoji_id:
                        try:
                            emoji_id = int(emoji_id)
                        except ValueError:
                            pass
                    
                    reconstructed_entities.append(MessageEntity(
                        type=entity_type,
                        offset=e.get("offset"),
                        length=e.get("length"),
                        url=e.get("url"),
                        custom_emoji_id=emoji_id,
                        language=e.get("language")
                    ))
                entities = reconstructed_entities

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
            elif content_type == "animation":
                return await client.send_animation(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities)
            elif content_type == "voice":
                return await client.send_voice(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities)
            elif content_type == "sticker":
                return await client.send_sticker(channel_id, file_id, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error sending post to {channel_id}: {e}")
            raise

post_service = PostService()
