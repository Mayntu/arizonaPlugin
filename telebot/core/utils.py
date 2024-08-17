from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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

