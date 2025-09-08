from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from config import settings

class AdminOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[..., Awaitable[Any]],
        event: object,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        else:
            # На всякий случай пропускаем неизвестные типы событий
            return await handler(event, data)

        if user_id not in settings.ADMIN_IDS:
            if isinstance(event, CallbackQuery):
                # Важно ответить на колбэк, чтобы не крутился спиннер
                await event.answer("Доступ запрещён", show_alert=True)
            elif isinstance(event, Message):
                await event.answer("Доступ запрещён.")
            return  # Прерываем обработку

        return await handler(event, data)
