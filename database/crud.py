from typing import List, Optional, Dict, Any
from config import settings
from .connection import db
from .local_db import local_db
from .models import User, Channel, Post
from datetime import datetime

class CRUD:
    def __init__(self):
        self.use_mongo = settings.USE_MONGODB

    # User Operations
    async def get_user(self, user_id: int) -> Optional[Dict]:
        if self.use_mongo:
            return await db.db.users.find_one({"user_id": user_id})
        return await local_db.find_one("users", {"user_id": user_id})

    async def create_user(self, user_data: User):
        if self.use_mongo:
            await db.db.users.update_one(
                {"user_id": user_data.user_id},
                {"$set": user_data.dict()},
                upsert=True
            )
        else:
            await local_db.update_one("users", {"user_id": user_data.user_id}, {"$set": user_data.dict()}, upsert=True)

    # Channel Operations
    async def add_channel(self, channel_data: Channel):
        if self.use_mongo:
            await db.db.channels.update_one(
                {"channel_id": channel_data.channel_id},
                {"$set": channel_data.dict()},
                upsert=True
            )
        else:
            await local_db.update_one("channels", {"channel_id": channel_data.channel_id}, {"$set": channel_data.dict()}, upsert=True)

    async def get_channels(self, user_id: int) -> List[Dict]:
        if self.use_mongo:
            return await db.db.channels.find({"owner_id": user_id}).to_list(length=None)
        all_channels = await local_db.find("channels")
        return [ch for ch in all_channels if int(ch.get("owner_id")) == int(user_id)]

    async def get_channel(self, channel_id: int, user_id: int) -> Optional[Dict]:
        if self.use_mongo:
            return await db.db.channels.find_one({"channel_id": channel_id, "owner_id": user_id})
        all_channels = await local_db.find("channels")
        for ch in all_channels:
            if int(ch.get("channel_id")) == int(channel_id) and int(ch.get("owner_id")) == int(user_id):
                return ch
        return None

    async def remove_channel(self, channel_id: int, user_id: int):
        if self.use_mongo:
            await db.db.channels.delete_one({"channel_id": channel_id, "owner_id": user_id})
        else:
            await local_db.delete_one("channels", {"channel_id": channel_id, "owner_id": user_id})

    async def get_channel_by_id(self, channel_id: int) -> Optional[Dict]:
        if self.use_mongo:
            return await db.db.channels.find_one({"channel_id": channel_id})
        all_channels = await local_db.find("channels")
        for ch in all_channels:
            if int(ch.get("channel_id")) == int(channel_id):
                return ch
        return None

    # Post Operations
    async def create_post(self, post_data: Post):
        if self.use_mongo:
            result = await db.db.posts.insert_one(post_data.dict())
            return str(result.inserted_id)
        else:
            doc = await local_db.insert_one("posts", post_data.dict())
            return doc["_id"]

    async def get_scheduled_posts(self):
        now = datetime.utcnow()
        if self.use_mongo:
            return await db.db.posts.find({
                "status": "scheduled",
                "scheduled_at": {"$lte": now}
            }).to_list(length=None)
        else:
            all_posts = await local_db.find("posts")
            return [
                p for p in all_posts 
                if p.get("status") == "scheduled" and p.get("scheduled_at") and p["scheduled_at"] <= now
            ]

    async def update_post_status(self, post_id: str, status: str):
        if self.use_mongo:
            from bson import ObjectId
            await db.db.posts.update_one(
                {"_id": ObjectId(post_id)},
                {"$set": {"status": status}}
            )
        else:
            await local_db.update_one("posts", {"_id": post_id}, {"$set": {"status": status}})

crud = CRUD()
