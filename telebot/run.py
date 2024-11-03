from aiogram import Dispatcher

from core.bot import bot
from controllers.main_controller import main_router
from controllers.admin_controller import router as admin_router

import asyncio
import logging


logging.basicConfig(level=logging.INFO)

dp : Dispatcher = Dispatcher()
dp.include_routers(main_router, admin_router)


async def start_polling():
    while True:
        try:
            await dp.start_polling(bot, timeout=30)
        except Exception as e:
            logging.error(f"polling error: {e}")
            await asyncio.sleep(5)
        else:
            break



async def main():
    await start_polling()


if __name__ == "__main__":
    asyncio.run(main=main())