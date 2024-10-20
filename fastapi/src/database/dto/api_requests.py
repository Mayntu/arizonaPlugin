from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional

from src.database.schemas.payday_stats_schema import PaydayStatSchema

class HwidRequest(BaseModel):
    hwid : str


class ValidateTokenRequest(HwidRequest):
    ...


class GetCaptchasRequest(HwidRequest):
    zero_chance : int
    count : int


class ConvertTimeRequest(HwidRequest):
    time : str | int
    isNumber : bool
    offset : int


class CheckServerRequest(HwidRequest):
    server_ip : str


class CheckServerInServersRequest(HwidRequest):
    allowed_server_ips : list[str]
    server_ip : str


class CalcTaxRequest(HwidRequest):
    calcInMskTime: bool
    nalogNow: int
    nalogInHour: int
    property: str
    insurance: bool
    time : int
    timeOffset : int


# class SearchPropertyEnum(str, Enum):
#     houses = "HOUSES"
#     businesses = "BUSINESSES"

# class HasPropertyEnum(str, Enum):
#     no_matter = "NOMATTER"
#     has_property = "HASPROPERTY"
#     no_property = "NOPROPERTY"

class SearchPropertyRequest(HwidRequest):
    # start : int
    # end : int
    # propertyAmount : int
    serverNumber : int
    # searchInRange : bool
    # searchProperties : SearchPropertyEnum
    # hasProperty : HasPropertyEnum


class PaydayStatPostRequest(HwidRequest):
    server_name : str
    properties : list[PaydayStatSchema.Property]
    page_number : Optional[int]

    model_config = ConfigDict(str_to_lower=True)


class PaydayStatGetByServerNameRequest(HwidRequest):
    server_name : str

    model_config = ConfigDict(str_to_lower=True)
