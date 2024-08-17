from aiogram import Bot
from core.settings import BOT_TOKEN

import logging

logging.basicConfig(level=logging.INFO)

bot : Bot = Bot(token=BOT_TOKEN)