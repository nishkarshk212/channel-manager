import asyncio
from concurrent.futures import ThreadPoolExecutor
from telegraph import Telegraph
from utils.logger import logger

class TelegraphService:
    def __init__(self):
        self.telegraph = None
        self._initialized = False
        self._executor = ThreadPoolExecutor(max_workers=5)

    def _lazy_init(self):
        if not self._initialized:
            try:
                self.telegraph = Telegraph()
                self.telegraph.create_account(short_name='ChannelManagerBot')
                self._initialized = True
                logger.info("Telegraph service initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Telegraph (Network Issue?): {e}")

    async def create_page(self, title: str, html_content: str):
        # Run synchronous telegraph calls in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor, 
            self._sync_create_page, 
            title, 
            html_content
        )

    def _sync_create_page(self, title: str, html_content: str):
        self._lazy_init()
        if not self.telegraph:
            return None
        try:
            response = self.telegraph.create_page(
                title=title,
                html_content=html_content
            )
            return f"https://telegra.ph/{response['path']}"
        except Exception as e:
            logger.error(f"Telegraph Error: {e}")
            return None

telegraph_service = TelegraphService()
