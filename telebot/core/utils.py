from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.settings import FLASK_URL, TOKEN_PASS

import httpx


def create_keyboard(url : str, uuid : str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оплатить", url=url),
                InlineKeyboardButton(text="Проверить", callback_data=f"payment_uuid_{uuid}")
            ]
        ]
    )
    return keyboard


async def get_token() -> str:
    data : dict = {
        "secret" : TOKEN_PASS
    }
    response = await make_post_request(url=FLASK_URL + "/token", data=data)
    if response.status_code == 200 or response.status_code == 201:
        data : dict = response.json()
        return data.get("token_id")
    
    return None


async def make_post_request(url : str, data : dict = None):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        return response
