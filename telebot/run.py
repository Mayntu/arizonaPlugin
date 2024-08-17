from aiogram import Dispatcher

from core.bot import bot
from controllers.main_controller import main_router

import asyncio


dp : Dispatcher = Dispatcher()
dp.include_router(main_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main=main())