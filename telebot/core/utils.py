from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pymongo import ASCENDING as ASC, DESCENDING as DESC
from datetime import datetime
from bson import ObjectId

from core.settings import (
    FASTAPI_URL,
    TOKEN_PASS,
    REQUEST_LIMIT_TTL,
    RedisKeys
)
from core.pay_yoomoney import (
    insert_token_in_buy_schema
)

from database.settings import (
    reports_table
)
from database.schemas.report_schema import ReportSchema

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
            KeyboardButton(text="/report 📝")
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


async def report(user_id : int) -> int:
    key : str = f"report_limit:{user_id}"
    last_report_time = await redis.ttl(key)

    if not await redis.exists(key):
        await redis.set(key, "1", ex=300)

    return last_report_time


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
    if await redis.exists(RedisKeys.reports.value):
        reports : str = json.dumps(await reports_table.find().sort("datetime", DESC).limit(10).to_list(length=None), default=json_serializer)
        await redis.set(RedisKeys.reports.value, reports, ex=600)
    
    return inserted_report.inserted_id
