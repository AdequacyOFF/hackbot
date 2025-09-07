import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import settings
from persistence.db import init_schema

# Импортируйте свои роутеры после разнесения логики:
# from bot.handlers import common, participant_apply, participant_results, participant_suggest, admin

async def main():
    if not settings.BOT_TOKEN:
        raise RuntimeError("Set BOT_TOKEN in .env")
    init_schema()
    bot = Bot(settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # dp.include_router(common.router)
    # dp.include_router(participant_apply.router)
    # dp.include_router(participant_results.router)
    # dp.include_router(participant_suggest.router)
    # dp.include_router(admin.router)

    # Временно можно подключить ваш монолитный router тут, если он у вас в одном файле.

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())