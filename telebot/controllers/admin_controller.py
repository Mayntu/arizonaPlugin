from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from core.admin_utils import (
    admin_required,
    get_pagination_keyboard,
    get_all_reports
)
from core.bot import bot


router : Router = Router()

REPORT_TEXT : str = """Репорт #{report_id}
@{user_login} (id {user_id}) {report_datetime}
Имя аккаунта {user_fullname}

    {report_text}
"""


@router.message(Command(commands=["allreports", "allrs"]))
@admin_required
async def all_reports(message : Message):
    await show_page(message=message, reports=await get_all_reports())


async def show_page(message : Message, reports : list, page_number : int = 1, query : CallbackQuery = None):
    if not len(reports) > 0:
        await message.answer(text="Репортов нет")
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
    
    pagination_reply = get_pagination_keyboard(current_page=page_number, total_pages=len(reports))

    if not query:
        await message.answer(text=report_text, reply_markup=pagination_reply)
    else:
        await query.message.edit_text(text=report_text, reply_markup=pagination_reply)


@router.callback_query(lambda q: "page_number_" in q.data)
async def report_paginate(query : CallbackQuery):
    page_number : int = int(query.data.split("page_number_")[1])
    reports : list = await get_all_reports()
    await show_page(message=query.message, reports=reports, page_number=page_number, query=query)


@router.callback_query(lambda q: q.data == "ignore")
async def ignore(query : CallbackQuery):
    await query.answer(text="")
