from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from core.bot import bot
from core.settings import (
    ADMIN_CHAT_IDS,
    WELCOME_TEXT,
    INFO_TEXT,
    LICENSE_TEXT,
    BUY_TEXT,
    REPORT_COMMAND_TEXT,
    IDEA_COMMAND_TEXT
)
from core.pay_yoomoney import (
    get_ticket,
    check_payment
)
from core.utils import (
    create_keyboard,
    get_token,
    start_keyboard,
    is_rate_limited,
    check_report_timeout,
    check_idea_timeout,
    save_report_to_db,
    save_idea_to_db,
    undo_keyboard,
    send_script_file
)
from database.schemas.report_schema import ReportSchema
from database.schemas.idea_schema import IdeaSchema

main_router : Router = Router()


class ReportStates(StatesGroup):
    waiting_for_report = State()
    waiting_for_idea   = State()



@main_router.message(Command(commands=["start"]))
async def start_command_handler(message : Message):
    await message.answer(WELCOME_TEXT, reply_markup=start_keyboard())


@main_router.message(Command(commands=["info"]))
async def info_command_handler(message : Message):
    await bot.send_message(chat_id=message.chat.id, text=INFO_TEXT, parse_mode="Markdown")


@main_router.message(Command(commands=["license"]))
async def license_command_handler(message : Message):
    await bot.send_message(chat_id=message.chat.id, text=LICENSE_TEXT, parse_mode="Markdown")


@main_router.message(Command(commands=["buy"]))
async def buy_handler(message : Message):
    user_id = message.from_user.id
    
    try:
        is_limitted, ttl = await is_rate_limited(user_id)
    except Exception as e:
        print(f"redis not working - {e}")
        is_limitted = False
        for admin in ADMIN_CHAT_IDS:
            await bot.send_message(admin, text="редис не работает нужен фикс!!!!!!!!!!")
    
    if is_limitted:
        await message.answer(f"Вы уже запросили покупку. Подождите {ttl} секунд перед следующим запросом.")
        return
    
    payment_uuid, link = get_ticket()
    await bot.send_message(
        chat_id=message.chat.id,
        text=BUY_TEXT,
        reply_markup=create_keyboard(url=link, uuid=payment_uuid)
    )


@main_router.callback_query(lambda c: "payment_uuid_" in c.data)
async def callback_check_payment(callback_query : CallbackQuery):
    uuid : str = callback_query.data.split("payment_uuid_")[1]
    if await check_payment(uuid=uuid, user_id=str(callback_query.from_user.id)):
        await bot.send_message(callback_query.from_user.id, "Не оплачено")
    else:
        token : str = await get_token(buy_uuid=uuid)
        await bot.send_message(callback_query.from_user.id, f"Ваш токен : {token}")
        await send_script_file(bot=bot, chat_id=callback_query.from_user.id)

        await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=None)
        
        for admin_chat_id in ADMIN_CHAT_IDS:
            await bot.send_message(chat_id=admin_chat_id, text=f"Был куплен токен : {token}")


@main_router.message(Command(commands=['report']))
async def report_bug(message: Message, state : FSMContext):
    user_id : int = message.from_user.id
    
    report_timeout : int = await check_report_timeout(user_id=user_id, set_timeout=False)

    if report_timeout > 0:
        await message.reply(f"Вы можете отправить новый отчет через {int(report_timeout)} секунд.")
        return
    
    await message.reply(REPORT_COMMAND_TEXT, parse_mode="Markdown", reply_markup=undo_keyboard())
    await state.set_state(ReportStates.waiting_for_report)


@main_router.message(Command(commands=['idea']))
async def scripts_idea(message: Message, state : FSMContext):
    user_id : int = message.from_user.id
    
    idea_timeout : int = await check_idea_timeout(user_id=user_id, set_timeout=False)

    if idea_timeout > 0:
        await message.reply(f"Вы можете отправить новую идею через {int(idea_timeout)} секунд.")
        return
    
    await message.reply(IDEA_COMMAND_TEXT, parse_mode="Markdown", reply_markup=undo_keyboard())
    await state.set_state(ReportStates.waiting_for_idea)


@main_router.message(Command(commands=['undo']))
async def undo_command_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state is None:
        await message.reply("Нет активных действий для отмены.")
    else:
        await state.clear()
        await message.reply("Отменено")


@main_router.message(ReportStates.waiting_for_report)
async def handle_report_response(message: Message, state : FSMContext):
    user_id = message.from_user.id
    report_message = message.text

    await check_report_timeout(user_id=user_id, set_timeout=True)

    inserted_id : str = str(await save_report_to_db(
        report_schema=ReportSchema(
            user_id=user_id,
            user_fullname=message.from_user.full_name,
            user_login=message.from_user.username or "hidden",
            message=message.text,
            datetime=datetime.now()
        )
    ))

    for admin in ADMIN_CHAT_IDS:
        await bot.send_message(chat_id=admin, text=f"Отчет номер - {inserted_id} от пользователя @{message.from_user.username or "hidden"} id #{user_id} \n {report_message}")
    await message.reply("Ваш отчет успешно отправлен. Спасибо!")

    await state.clear()


@main_router.message(ReportStates.waiting_for_idea)
async def handle_idea_response(message: Message, state : FSMContext):
    user_id = message.from_user.id
    idea_message = message.text

    await check_idea_timeout(user_id=user_id, set_timeout=True)

    inserted_id : str = str(await save_idea_to_db(
        idea_schema=IdeaSchema(
            user_id=user_id,
            user_fullname=message.from_user.full_name,
            user_login=message.from_user.username or "hidden",
            message=message.text,
            datetime=datetime.now()
        )
    ))

    for admin in ADMIN_CHAT_IDS:
        await bot.send_message(chat_id=admin, text=f"Идея номер - {inserted_id} от пользователя @{message.from_user.username or "hidden"} id #{user_id} \n {idea_message}")
    await message.reply("Ваша идея успешно отправлена. Спасибо!")

    await state.clear()


@main_router.callback_query(lambda c: c.data == "undo")
async def undo_cb_handler(callback_query: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.edit_text("Отменено")
