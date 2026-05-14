from hydrogram import Client, types
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
        entities: Optional[List[types.MessageEntity]] = None,
        from_chat_id: Optional[int] = None,
        message_id: Optional[int] = None
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
                chat = await client.get_chat(channel_id)
                logger.info(f"Successfully resolved chat {channel_id}: {chat.title}")
            except Exception as e:
                logger.warning(f"Could not pre-resolve chat {channel_id} by ID: {e}")
                # Try resolving via username from DB if ID fails
                channel_data = await crud.get_channel_by_id(channel_id) if isinstance(channel_id, int) else None
                if channel_data:
                    logger.info(f"Found channel data in DB: {channel_data.get('title')} (Username: @{channel_data.get('username')})")
                    if channel_data.get("username"):
                        username = channel_data["username"]
                        logger.info(f"Attempting to resolve chat via username: @{username}")
                        try:
                            chat = await client.get_chat(username)
                            channel_id = chat.id  # Update ID to the resolved one
                            logger.info(f"Resolved @{username} to ID: {channel_id}")
                        except Exception as e2:
                            logger.error(f"Failed to resolve chat via username @{username}: {e2}")
                else:
                    logger.error(f"Channel {channel_id} not found in database!")

            # Use copy_message if possible to preserve premium emojis
            if from_chat_id and message_id:
                try:
                    logger.info(f"Using copy_message to preserve premium emojis from {from_chat_id}:{message_id}")
                    return await client.copy_message(
                        chat_id=channel_id,
                        from_chat_id=from_chat_id,
                        message_id=message_id,
                        caption=caption,
                        reply_markup=reply_markup
                    )
                except Exception as copy_err:
                    logger.warning(f"copy_message failed, falling back to normal send: {copy_err}")

            # Convert dict entities back to MessageEntity if necessary
            if entities and isinstance(entities, list) and isinstance(entities[0], dict):
                from hydrogram.types import MessageEntity
                from hydrogram.enums import MessageEntityType
                
                reconstructed_entities = []
                for e in entities:
                    # Map string type back to Enum if possible
                    entity_type = e.get("type")
                    if isinstance(entity_type, str):
                        try:
                            # Handle custom_emoji specifically
                            if entity_type == "custom_emoji":
                                entity_type = MessageEntityType.CUSTOM_EMOJI
                            # Handle blockquote and other potential newer types
                            elif entity_type == "blockquote":
                                try:
                                    entity_type = MessageEntityType.BLOCKQUOTE
                                except AttributeError:
                                    logger.warning("BLOCKQUOTE entity type not supported by this Hydrogram version")
                                    continue
                            else:
                                try:
                                    entity_type = getattr(MessageEntityType, entity_type.upper())
                                except AttributeError:
                                    logger.warning(f"Entity type {entity_type} not supported by this Hydrogram version")
                                    continue
                        except Exception as exc:
                            logger.error(f"Error mapping entity type {entity_type}: {exc}")
                            continue
                    
                    # Ensure custom_emoji_id is an integer (fixes 'to_bytes' error)
                    emoji_id = e.get("custom_emoji_id")
                    if emoji_id:
                        try:
                            emoji_id = int(emoji_id)
                            # If it's a custom emoji, force the type if it was missed
                            if not isinstance(entity_type, MessageEntityType) or entity_type != MessageEntityType.CUSTOM_EMOJI:
                                entity_type = MessageEntityType.CUSTOM_EMOJI
                        except (ValueError, TypeError):
                            emoji_id = None
                    
                    # Only add if entity_type is a valid Enum member
                    if isinstance(entity_type, MessageEntityType):
                        reconstructed_entities.append(MessageEntity(
                            type=entity_type,
                            offset=int(e.get("offset", 0)),
                            length=int(e.get("length", 0)),
                            url=e.get("url"),
                            custom_emoji_id=emoji_id,
                            language=e.get("language"),
                            client=client
                        ))
                    else:
                        logger.warning(f"Skipping entity due to invalid type: {entity_type}")
                
                entities = reconstructed_entities
                logger.info(f"Reconstructed {len(entities)} entities for sending")

            # Determine parse_mode. If we have entities, we don't need parse_mode.
            # If we don't have entities, we'll try HTML to support cases where users send tags.
            parse_mode = None if entities else "html"

            if content_type == "text":
                return await client.send_message(channel_id, caption, reply_markup=reply_markup, entities=entities, parse_mode=parse_mode)
            elif content_type == "photo":
                return await client.send_photo(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities, parse_mode=parse_mode)
            elif content_type == "video":
                return await client.send_video(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities, parse_mode=parse_mode)
            elif content_type == "document":
                return await client.send_document(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities, parse_mode=parse_mode)
            elif content_type == "audio":
                return await client.send_audio(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities, parse_mode=parse_mode)
            elif content_type == "animation":
                return await client.send_animation(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities, parse_mode=parse_mode)
            elif content_type == "voice":
                return await client.send_voice(channel_id, file_id, caption=caption, reply_markup=reply_markup, caption_entities=entities, parse_mode=parse_mode)
            elif content_type == "sticker":
                return await client.send_sticker(channel_id, file_id, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error sending post to {channel_id}: {e}")
            raise

post_service = PostService()
