import json
import os
import asyncio
from typing import Dict, List, Any, Optional
from utils.logger import logger

class LocalDB:
    def __init__(self, folder: str = "data"):
        self.folder = folder
        self.data: Dict[str, List[Dict[str, Any]]] = {
            "users": [],
            "channels": [],
            "posts": []
        }
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        
        self.load_all()

    def get_file_path(self, collection: str):
        return os.path.join(self.folder, f"{collection}.json")

    def load_all(self):
        for collection in self.data.keys():
            path = self.get_file_path(collection)
            if os.path.exists(path):
                with open(path, "r") as f:
                    try:
                        self.data[collection] = json.load(f)
                    except json.JSONDecodeError:
                        self.data[collection] = []
            else:
                self.save(collection)

    def save(self, collection: str):
        path = self.get_file_path(collection)
        with open(path, "w") as f:
            json.dump(self.data[collection], f, indent=4, default=str)

    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for item in self.data.get(collection, []):
            if all(item.get(k) == v for k, v in query.items()):
                return item
        return None

    async def find(self, collection: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if not query:
            return self.data.get(collection, [])
        
        results = []
        for item in self.data.get(collection, []):
            if all(item.get(k) == v for k, v in query.items()):
                results.append(item)
        return results

    async def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        item = await self.find_one(collection, query)
        if item:
            if "$set" in update:
                item.update(update["$set"])
            else:
                item.update(update)
        elif upsert:
            new_item = query.copy()
            if "$set" in update:
                new_item.update(update["$set"])
            else:
                new_item.update(update)
            # Ensure ID is string for consistency
            if "channel_id" in new_item:
                new_item["channel_id"] = int(new_item["channel_id"])
            self.data[collection].append(new_item)
        
        self.save(collection)

    async def insert_one(self, collection: str, document: Dict[str, Any]):
        if "_id" not in document:
            from bson import ObjectId
            document["_id"] = str(ObjectId())
        self.data[collection].append(document)
        self.save(collection)
        return document

    async def delete_one(self, collection: str, query: Dict[str, Any]):
        initial_len = len(self.data[collection])
        self.data[collection] = [
            item for item in self.data[collection]
            if not all(item.get(k) == v for k, v in query.items())
        ]
        if len(self.data[collection]) != initial_len:
            self.save(collection)

local_db = LocalDB()
