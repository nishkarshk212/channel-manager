from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.crud import crud
from services.post_service import post_service
from utils.logger import logger
from hydrogram import Client, types
from datetime import datetime

class Scheduler:
    def __init__(self, client: Client):
        self.client = client
        self.scheduler = AsyncIOScheduler()

    async def check_scheduled_posts(self):
        posts = await crud.get_scheduled_posts()
        for post in posts:
            try:
                reply_markup = None
                if post.get("buttons"):
                    kb = []
                    for btn in post["buttons"]:
                        kb.append([types.InlineKeyboardButton(btn["text"], url=btn["url"])])
                    reply_markup = types.InlineKeyboardMarkup(kb)

                for channel_id in post["channel_ids"]:
                    await post_service.send_to_channel(
                        self.client,
                        channel_id,
                        post["content_type"],
                        post.get("media_file_id"),
                        post.get("caption"),
                        reply_markup=reply_markup,
                        entities=post.get("entities"),
                        from_chat_id=post.get("from_chat_id"),
                        message_id=post.get("message_id"),
                        entities_match_msg=post.get("entities_match_msg", False)
                    )
                await crud.update_post_status(str(post["_id"]), "published")
                logger.info(f"Scheduled post {post['_id']} published")
            except Exception as e:
                logger.error(f"Failed to publish scheduled post {post['_id']}: {e}")

    def start(self):
        self.scheduler.add_job(self.check_scheduled_posts, "interval", minutes=1)
        self.scheduler.start()
        logger.info("Scheduler started")
