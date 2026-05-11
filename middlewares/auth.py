from hydrogram import filters
from database.crud import crud
from config import settings
from utils.logger import logger

async def is_admin_check(_, __, message):
    if not message.from_user:
        return False
        
    if message.from_user.id == settings.OWNER_ID:
        return True
    
    user = await crud.get_user(message.from_user.id)
    if user and user.get("role") in ["owner", "admin"]:
        return True
    
    logger.warning(f"Unauthorized admin access attempt by {message.from_user.id}")
    return False

is_admin = filters.create(is_admin_check)

async def is_editor_check(_, __, message):
    if not message.from_user:
        return False

    if message.from_user.id == settings.OWNER_ID:
        return True
    
    user = await crud.get_user(message.from_user.id)
    if user and user.get("role") in ["owner", "admin", "editor"]:
        return True
    
    logger.warning(f"Unauthorized editor access attempt by {message.from_user.id}")
    return False

is_editor = filters.create(is_editor_check)
