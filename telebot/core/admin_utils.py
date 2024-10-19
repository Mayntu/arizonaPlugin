from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import ASCENDING as ASC, DESCENDING as DESC
from bson import ObjectId

from core.utils import (
    redis,
    json_serializer,
    json_deserializer
)
from core.settings import (
    ADMIN_CHAT_IDS,
    RedisKeys
)

from database.settings import (
    reports_table,
)
from database.schemas.report_schema import ReportSchema

import json


def admin_required(func):
    async def wrapper(message : Message, *args):
        if str(message.from_user.id) not in ADMIN_CHAT_IDS:
            await message.reply("Ты кто?")
            return
        return await func(message, *args)
    return wrapper


def get_pagination_keyboard(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard : list[InlineKeyboardButton] = []
    
    if current_page > 1:
        keyboard.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_number_{current_page - 1}"))
    
    keyboard.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="ignore"))
    
    if current_page < total_pages:
        keyboard.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_number_{current_page + 1}"))
    
    return InlineKeyboardMarkup(inline_keyboard=[keyboard])



async def get_all_reports() -> list:
    if not await redis.exists(RedisKeys.reports.value):
        reports = await reports_table.find().sort("datetime", DESC).limit(10).to_list(length=None)
        reports_json = json.dumps(reports, default=json_serializer)
        await redis.set(RedisKeys.reports.value, reports_json, ex=600)
        return reports
    
    return json_deserializer(await redis.get(RedisKeys.reports.value))
