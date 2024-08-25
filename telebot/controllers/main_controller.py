from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    LabeledPrice,
    CallbackQuery,
)

from core.bot import bot
from core.pay_yoomoney import (
    get_ticket,
    check_payment
)
from core.utils import (
    create_keyboard,
    get_token
)

main_router : Router = Router()


PRICE : LabeledPrice = LabeledPrice(label="Подписка на 1 месяц", amount=100*100) # 100 RU


@main_router.message(Command(commands=["start"]))
async def start_command_handler(message : Message):
    await bot.send_message(message.chat.id, "test")

# @main_router.message(Command(commands=['buy']))
# async def buy_handler(message: Message):
#     if PAYMASTER_TOKEN.split(':')[1] == 'TEST':
#         await bot.send_message(message.chat.id, "Тестовый платеж!!!")
 
#     await bot.send_invoice(message.chat.id,
#                            title="Подписка на бота",
#                            description="Активация подписки на бота на 1 месяц",
#                            provider_token=PAYMASTER_TOKEN,
#                            currency="rub",
#                            photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
#                            photo_width=416,
#                            photo_height=234,
#                            photo_size=416,
#                            is_flexible=False,
#                            prices=[PRICE],
#                            start_parameter="one-month-subscription",
#                            payload="test-invoice-payload")


# @main_router.pre_checkout_query(lambda query: True)
# async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# @main_router.message(SuccessfulPayment)
# async def successful_payment(message: Message):
#     print("SUCCESSFUL PAYMENT:")
#     payment_info = message.successful_payment.to_python()
#     for k, v in payment_info.items():
#         print(f"{k} = {v}")
 
#     await bot.send_message(message.chat.id,
#                            f"Платёж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")


@main_router.message(Command(commands=["buy"]))
async def buy_handler(message : Message):
    payment_uuid, link = get_ticket()
    await bot.send_message(
        chat_id=message.chat.id,
        text="Кнопки для оплаты",
        reply_markup=create_keyboard(
            url=link,
            uuid=payment_uuid
        )
    )


@main_router.callback_query(lambda c: "payment_uuid_" in c.data)
async def callback_check_payment(callback_query : CallbackQuery):
    uuid : str = callback_query.data.split("payment_uuid_")[1]
    if await check_payment(uuid=uuid, user_id=str(callback_query.from_user.id)):
        token : str = await get_token()
        await bot.send_message(callback_query.from_user.id, f"Ваш токен : {token}")
    else:
        await bot.send_message(callback_query.from_user.id, "Не оплачено")


# @main_router.message()
# async def message_handler(message : Message):
#     await bot.send_message(message.chat.id, message.text)