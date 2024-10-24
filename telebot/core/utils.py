from aiogram import Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message, FSInputFile
from pymongo import ASCENDING as ASC, DESCENDING as DESC
from datetime import datetime
from uuid import uuid4
from bson import ObjectId
from urllib.parse import unquote
from aiohttp import ClientSession
from os import remove

from core.settings import (
    FASTAPI_URL,
    TOKEN_PASS,
    REQUEST_LIMIT_TTL,
    REPORTS_TIMEOUT,
    IDEAS_TIMEOUT,
    SCRIPT_DRIVE_URL,
    RedisKeys
)
from core.pay_yoomoney import (
    insert_token_in_buy_schema
)

from database.settings import (
    reports_table,
    ideas_table
)
from database.schemas.report_schema import ReportSchema
from database.schemas.idea_schema import IdeaSchema

import httpx
import json
import redis.asyncio as aioredis


try:
    redis = aioredis.from_url("redis://redis", decode_responses=True)
except Exception as e:
    print(f"redis not connecting - {e}")



def start_keyboard():
    keyboard : list[list[KeyboardButton]] = [
        [
            KeyboardButton(text="/buy 💸"),
            KeyboardButton(text="/info ℹ️"),
            KeyboardButton(text="/license 📜"),
            KeyboardButton(text="/report 📝"),
            KeyboardButton(text="/idea 💡")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)



def create_keyboard(url : str, uuid : str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Оплатить", url=url),
                InlineKeyboardButton(text="🔍 Проверить", callback_data=f"payment_uuid_{uuid}")
            ]
        ]
    )
    return keyboard


def undo_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="undo")]
        ]
    )


async def get_token(buy_uuid : str) -> str:
    data : dict = {
        "secret" : TOKEN_PASS
    }
    response = await make_post_request(url=FASTAPI_URL + "/api/v1/token", data=data)
    if response.status_code == 200 or response.status_code == 201:
        data : dict = response.json()
        await insert_token_in_buy_schema(
            schema_uuid=buy_uuid,
            token=data.get("token_id")
        )
        return data.get("token_id")
    
    return None


async def make_post_request(url : str, data : dict = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        return response



async def is_rate_limited(user_id: int) -> tuple:
    """
    Проверка, есть ли ограничение по времени для данного пользователя.
    Если запрос разрешен, обновляем TTL в Redis.
    """
    key = f"user:{user_id}:buy_limit"
    ttl : int = await redis.ttl(key)
    if await redis.exists(key):
        return True, ttl
    else:
        await redis.set(key, "limited", ex=REQUEST_LIMIT_TTL)
        return False, 0


async def check_report_timeout(user_id : int, set_timeout : bool) -> int:
    key : str = f"report_limit:{user_id}"

    if not await redis.exists(key):
        if set_timeout:
            await redis.set(key, "1", ex=REPORTS_TIMEOUT)
        return 0

    return await redis.ttl(key)


async def check_idea_timeout(user_id : int, set_timeout : bool) -> int:
    key : str = f"idea_limit:{user_id}"

    if not await redis.exists(key):
        if set_timeout:
            await redis.set(key, "1", ex=IDEAS_TIMEOUT)
        return 0

    return await redis.ttl(key)


async def send_script_file(bot : Bot, chat_id : str):
    global SCRIPT_DRIVE_URL
    try:
        async with ClientSession() as session:
            async with session.get(SCRIPT_DRIVE_URL) as response:
                if response.status != 200:
                    await bot.send_message(chat_id=chat_id, text=f"Не удалось скачать файл. Статус: {response.status}")
                    return

                cd = response.headers.get('Content-Disposition')
                if cd:
                    file_name = cd.split("filename=")[-1].strip('"')
                    file_name_unquoted : str = unquote(file_name)
                    file_name = f"{uuid4()}_{file_name_unquoted}"
                else:
                    file_name : str = "downloaded_file"
                
                with open(file_name, "wb") as f:
                    f.write(await response.read())
                
    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"Ошибка при скачивании файла: {e}")
        return

    file_to_send : FSInputFile = FSInputFile(file_name, filename=file_name_unquoted)
    await bot.send_document(chat_id=chat_id, document=file_to_send, caption="Скрипт")

    remove(file_name)


def json_serializer(obj):
    
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M")
    if isinstance(obj, ObjectId):
        return str(obj)


def json_deserializer(data):
    def custom_decoder(obj):
        for key, value in obj.items():
            try:
                obj[key] = datetime.strptime(value, "%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                print("err")
        return obj

    return json.loads(data, object_hook=custom_decoder)


async def save_report_to_db(report_schema : ReportSchema) -> ObjectId:
    inserted_report = await reports_table.insert_one(report_schema.model_dump(by_alias=True))
    if await redis.exists(RedisKeys.REPORTS.key_name):
        reports : str = json.dumps(await reports_table.find({"is_active" : True}).sort("datetime", DESC).limit(10).to_list(length=None), default=json_serializer)
        await redis.set(RedisKeys.REPORTS.key_name, reports, ex=RedisKeys.REPORTS.key_duration)
    
    return inserted_report.inserted_id


async def save_idea_to_db(idea_schema : IdeaSchema) -> ObjectId:
    inserted_idea = await ideas_table.insert_one(idea_schema.model_dump(by_alias=True))
    if await redis.exists(RedisKeys.IDEAS.key_name):
        ideas : str = json.dumps(await ideas_table.find({"is_active" : True}).sort("datetime", DESC).limit(20).to_list(length=None), default=json_serializer)
        await redis.set(RedisKeys.IDEAS.key_name, ideas, ex=RedisKeys.IDEAS.key_duration)
    
    return inserted_idea.inserted_id

