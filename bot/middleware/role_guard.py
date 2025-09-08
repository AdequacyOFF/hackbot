from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Update
from config import settings

class AdminOnlyMiddleware(BaseMiddleware):
    """Пропускает апдейты только от админов для определённых роутеров."""
    def __init__(self):
        super().__init__()

    async def __call__(self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]], event: Update, data: Dict[str, Any]) -> Any:
        user_id = None
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id

        if user_id is None or user_id not in settings.ADMIN_IDS:
            # Можем вернуть молча, чтобы не засорять чат.
            return
        return await handler(event, data)