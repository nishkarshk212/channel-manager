from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class User(BaseModel):
    user_id: int
    username: Optional[str] = None
    role: str = "editor"  # owner, admin, editor
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = Field(default_factory=dict)

class Channel(BaseModel):
    channel_id: int
    owner_id: int  # The user who added this channel
    title: str
    username: Optional[str] = None
    authorized_by: int
    added_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = {
        "auto_caption": "",
        "watermark": False,
        "force_subscribe": False,
        "auto_delete_timer": 0,  # 0 means disabled
    }

class Post(BaseModel):
    post_id: Optional[str] = None
    user_id: int  # The user who created this post
    channel_ids: List[int]
    content_type: str  # text, photo, video, etc.
    media_file_id: Optional[str] = None
    from_chat_id: Optional[int] = None
    message_id: Optional[int] = None
    entities_match_msg: bool = False
    caption: Optional[str] = None
    entities: Optional[List[Dict[str, Any]]] = None
    buttons: List[Dict[str, str]] = []
    scheduled_at: Optional[datetime] = None
    status: str = "draft"  # draft, scheduled, published
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
