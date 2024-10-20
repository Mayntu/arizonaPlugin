from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import ASCENDING as ASC, DESCENDING as DESC

from core.utils import (
    redis,
    json_serializer,
    json_deserializer
)
from core.settings import (
    ADMIN_CHAT_IDS,
    REPORT_TEXT,
    IDEA_TEXT,
    RedisKeys,
    QueryDataKeys
)

from database.settings import (
    reports_table,
    ideas_table
)

import json


def admin_required(func):
    async def wrapper(message : Message, *args):
        if str(message.from_user.id) not in ADMIN_CHAT_IDS:
            await message.reply("Ты кто?")
            return
        return await func(message, *args)
    return wrapper


async def show_idea_page(message : Message, ideas : list, page_number : int = 1, query : CallbackQuery = None):
    if not len(ideas):
        await message.answer(QueryDataKeys.IDEAS.empty_array_text)
        return
    
    idea = ideas[page_number - 1]
    try:
        idea_datetime_str : str = idea.get("datetime").strftime("%Y-%d-%m %H:%M")
    except Exception as e:
        idea_datetime_str : str = ""
    
    idea_text : str = IDEA_TEXT.format(
        idea_id=idea.get("_id"),
        user_login=idea.get("user_login"),
        user_id=idea.get("user_id"),
        idea_datetime=idea_datetime_str,
        user_fullname=idea.get("user_fullname"),
        idea_text=idea.get("message")
    )
    
    await show_page(message=message, array=ideas, text=idea_text, data_type=QueryDataKeys.IDEAS, page_number=page_number, query=query)


async def show_report_page(message : Message, reports : list, page_number : int = 1, query : CallbackQuery = None):
    if not len(reports):
        await message.answer(text=QueryDataKeys.REPORTS.empty_array_text)
        return
    
    report = reports[page_number - 1]
    try:
        report_datetime_str : str = report.get("datetime").strftime("%Y-%d-%m %H:%M")
    except Exception as e:
        report_datetime_str : str = ""
    
    report_text : str = REPORT_TEXT.format(
        report_id=report.get("_id"),
        user_login=report.get("user_login"),
        user_id=report.get("user_id"),
        report_datetime=report_datetime_str,
        user_fullname=report.get("user_fullname"),
        report_text=report.get("message")
    )

    await show_page(message=message, array=reports, text=report_text, data_type=QueryDataKeys.REPORTS, page_number=page_number, query=query)


async def show_page(message : Message, array : list, text : str, data_type : QueryDataKeys, page_number : int = 1, query : CallbackQuery = None):
    pagination_reply = get_pagination_keyboard(current_page=page_number, total_pages=len(array), data_type=data_type)

    if not query:
        await message.answer(text=text, reply_markup=pagination_reply)
    else:
        await query.message.edit_text(text=text, reply_markup=pagination_reply)



def get_pagination_keyboard(current_page: int, total_pages: int, data_type : QueryDataKeys) -> InlineKeyboardMarkup:
    keyboard : list[InlineKeyboardButton] = []
    
    callback_data_page_up : str = data_type.page_number_key.format(current_page = current_page + 1)
    callback_data_page_down : str = data_type.page_number_key.format(current_page = current_page - 1)
    ignore_key : str = data_type.ignore_key
    
    if current_page > 1:
        keyboard.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=callback_data_page_down))
    
    keyboard.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data=ignore_key))
    
    if current_page < total_pages:
        keyboard.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=callback_data_page_up))
    
    return InlineKeyboardMarkup(inline_keyboard=[keyboard])



async def get_all_reports() -> list:
    if not await redis.exists(RedisKeys.REPORTS.key_name):
        reports = await reports_table.find({"is_active" : True}).sort("datetime", DESC).limit(10).to_list(length=None)
        reports_json = json.dumps(reports, default=json_serializer)
        await redis.set(RedisKeys.REPORTS.key_name, reports_json, ex=RedisKeys.REPORTS.key_duration)
        return reports
    
    return json_deserializer(await redis.get(RedisKeys.REPORTS.key_name))


async def get_all_ideas() -> list:
    if not await redis.exists(RedisKeys.IDEAS.key_name):
        ideas = await ideas_table.find({"is_active" : True}).sort("datetime", DESC).limit(20).to_list(length=None)
        ideas_json = json.dumps(ideas, default=json_serializer)
        await redis.set(RedisKeys.IDEAS.key_name, ideas_json, ex=RedisKeys.IDEAS.key_duration)
        return ideas
    
    return json_deserializer(await redis.get(RedisKeys.IDEAS.key_name))
