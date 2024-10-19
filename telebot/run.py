from aiogram import Dispatcher

from core.bot import bot
from controllers.main_controller import main_router
from controllers.admin_controller import router as admin_router

import asyncio


dp : Dispatcher = Dispatcher()
dp.include_routers(main_router, admin_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main=main())