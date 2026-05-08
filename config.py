import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/channel_manager")
    USE_MONGODB: bool = os.getenv("USE_MONGODB", "True").lower() == "true"
    
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    LOG_CHANNEL_ID: int = int(os.getenv("LOG_CHANNEL_ID", "0"))
    
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    class Config:
        env_file = ".env"

settings = Settings()
