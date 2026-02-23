import asyncio
import logging
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from src.handlers import router
from src.database import init_db

load_dotenv()

async def main():
    # Инициализируем базу данных
    init_db()

    bot_token = getenv("TOKEN")
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=bot_token)
    dp = Dispatcher()

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
