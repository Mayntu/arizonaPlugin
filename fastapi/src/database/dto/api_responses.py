from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from src.database.schemas.payday_stats_schema import PaydayStatSchema

class CalcTaxResponse(BaseModel):
    hours : int
    days : int
    leftHours : int
    date : str


class ExpireTimeResponse(BaseModel):
    date : str


class GetPaydayStatsByServerNameResponse(BaseModel):
    _id : UUID
    server_name : str
    properties : list[PaydayStatSchema.Property]
    datetime : str
    page_number : Optional[int]
