import asyncio
import os
from aiogram import Bot, Dispatcher, F
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from app.handlers import router
from database.models import async_main

bot: Bot = Bot(token=os.getenv("TOKEN"))
dp: Dispatcher = Dispatcher()


async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")
