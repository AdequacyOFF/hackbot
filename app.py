import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties  # <-- новое
from config import settings
from persistence.db import init_schema
from aiogram.fsm.storage.memory import MemoryStorage
from bot.handlers import common, participant_apply, participant_results, participant_suggest, admin
from bot.middleware.role_guard import AdminOnlyMiddleware

async def main():
    if not settings.BOT_TOKEN:
        raise RuntimeError("Set BOT_TOKEN in .env")

    init_schema()

    # aiogram >= 3.7: parse_mode через default=DefaultBotProperties(...)
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Пользовательские роутеры
    dp.include_router(common.router)
    dp.include_router(participant_apply.router)
    dp.include_router(participant_results.router)
    dp.include_router(participant_suggest.router)

    # Админский роутер — оборачиваем middleware-ом
    admin_router = admin.router
    admin_router.message.middleware(AdminOnlyMiddleware())
    admin_router.callback_query.middleware(AdminOnlyMiddleware())
    dp.include_router(admin_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
