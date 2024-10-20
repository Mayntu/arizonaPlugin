from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from core.settings import (
    QueryDataKeys
)
from core.admin_utils import (
    admin_required,
    show_report_page,
    show_idea_page,
    get_all_reports,
    get_all_ideas
)


router : Router = Router()

@router.message(Command(commands=["allreports", "allrs"]))
@admin_required
async def all_reports(message : Message):
    await show_report_page(message=message, reports=await get_all_reports())


@router.message(Command(commands=["allideas"]))
@admin_required
async def all_ideas(message : Message):
    await show_idea_page(message=message, ideas=await get_all_ideas())



@router.callback_query(lambda q: QueryDataKeys.REPORTS.page_number_key.format(current_page="") in q.data)
async def report_paginate(query : CallbackQuery):
    page_number : int = int(query.data.split(QueryDataKeys.REPORTS.page_number_key.format(current_page=""))[1])
    reports : list = await get_all_reports()
    await show_report_page(message=query.message, reports=reports, page_number=page_number, query=query)


@router.callback_query(lambda q: QueryDataKeys.IDEAS.page_number_key.format(current_page="") in q.data)
async def idea_paginate(query : CallbackQuery):
    page_number : int = int(query.data.split(QueryDataKeys.IDEAS.page_number_key.format(current_page=""))[1])
    ideas : list = await get_all_ideas()
    await show_idea_page(message=query.message, ideas=ideas, page_number=page_number, query=query)


@router.callback_query(lambda q: "ignore" in q.data)
async def ignore(query : CallbackQuery):
    await query.answer(text="")
