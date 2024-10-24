from fastapi import HTTPException
from random import randint
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from math import ceil, floor
from redis import asyncio as aioredis

from src.database.dto.api_requests import (
    GetCaptchasRequest, ConvertTimeRequest, CheckServerRequest, CheckServerInServersRequest, CalcTaxRequest, SearchPropertyRequest, PaydayStatPostRequest, PaydayStatGetByServerNameRequest
)
from src.database.dto.api_responses import (
    CalcTaxResponse
)
from src.database.settings import (
    MOSCOW_UTC_OFFSET,
    ARIZONA_SERVERS,
    ARIZONA_IP_LIST,
    ARIZONA_MAP_URL,
    ASC,
    DESC,
    PROPS,
    payday_stats_table
)
from src.database.schemas.payday_stats_schema import PaydayStatSchema

import requests
import httpx
import json



async def get_captchas(request : GetCaptchasRequest) -> list[str]:
    count : int = request.count
    zero_chance : int = request.zero_chance

    captchas : list[str] = []
    for i in range(0, count):
        captcha : str = str(randint(1, 9))
        for j in range(3):
            captcha += str(randint(0, 9))
        if zero_chance > randint(0, 100):
            captcha += "0"
            captchas.append(captcha)
            continue
        captcha += str(randint(0, 9))
        captchas.append(captcha)
        
    return captchas


async def convert_local_time_to_moscow(request : ConvertTimeRequest) -> int | str:
    if request.isNumber:
            seconds_since_epoch = int(request.time)
            local_time = datetime.fromtimestamp(seconds_since_epoch, tz=timezone(timedelta(hours=request.offset)))
    
    if not request.isNumber:
        local_time : datetime = datetime.strptime(request.time, "%H:%M:%S")

    try:
        moscow_time = local_time - timedelta(hours=request.offset - MOSCOW_UTC_OFFSET)

        print(f"User time: {local_time}")
        print(f"UTC offset: {request.offset}")
        print(f"MOSCOW time: {moscow_time}")

        return moscow_time.strftime("%H:%M:%S") + " MSK"
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="not valid format")


async def check_server_is_in_list(request : CheckServerRequest) -> bool:
    return request.server_ip in ARIZONA_IP_LIST


async def check_server_is_in_servers(request : CheckServerInServersRequest) -> bool:
    return request.server_ip in request.allowed_server_ips


async def calc_tax(request : CalcTaxRequest) -> CalcTaxResponse:
    nalog_now : int = request.nalogNow
    nalog_in_hour : int = request.nalogInHour * 2 if not request.insurance else request.nalogInHour
    time : int = request.time
    price : int = PROPS.HOUSE.price if request.property.upper() == PROPS.HOUSE.title else PROPS.BUSINESS.price
    time_offset : int = request.timeOffset

    hours : int = ceil((price - nalog_now) / nalog_in_hour)
    seconds_remaining : int = 3600 * hours
    days : int = floor(hours / 24)
    leftHours : int = hours - (days * 24)

    seconds_when_expire : int = time + seconds_remaining + (time_offset * 3600)

    tz : timezone = timezone.utc
    date : str = "{date}"
    if request.calcInMskTime:
        tz : timezone = timezone(timedelta(hours=3))
        seconds_when_expire : int = time + seconds_remaining
        date = "{date} MSK"
    
    date = date.format(date=datetime.strftime(datetime.fromtimestamp(seconds_when_expire, tz=tz), format="%d.%m.%Y %H:00"))

    calc_tax_response : CalcTaxResponse = CalcTaxResponse(
        hours=hours,
        days=days,
        leftHours=leftHours,
        date=date
    )

    return calc_tax_response


async def search_property(request : SearchPropertyRequest, redis : aioredis.Redis) -> dict:
    arizona_map_headers : dict = {
        "accept" : "application/json",
        "origin" : "https://arizona-rp.com/",
        "referer" : "https://arizona-rp.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    cache_key = f"arizona_map_{request.serverNumber}"
    cached_data = await redis.get(cache_key)
    print("first")

    if cached_data:
        print("Данные взяты из кэша")
        map_data = json.loads(cached_data)
    else:
        print("second")
        try:
            response : httpx.Response = await make_async_get_request(
                headers=arizona_map_headers,
                url=ARIZONA_MAP_URL + f"/{request.serverNumber}"
            )
        except Exception as e:
            print(f"exception : {e}")
            raise HTTPException(status_code=500, detail="arizona map api not working")

        if not response.status_code in range(190, 230):
            print(f"exception | status_code : {response.status_code}")
            raise HTTPException(status_code=500, detail="arizona map api not working")
        
        print("go")
        map_data: dict = response.json()

        print("redis")

        # кэшируем данные на 10 минут (600 секунд)
        await redis.setex(cache_key, 600, json.dumps(map_data))
        print("nice")


    props : list[dict] = map_data["houses"]["onAuction"] + map_data["houses"]["hasOwner"] + map_data["businesses"]["onAuction"]

    for prop in map_data["businesses"]["noAuction"]:
        props += map_data["businesses"]["noAuction"][prop]


    owners_info : dict = {}
    for entry in props:
        owner = entry["owner"]
        owner_id = entry["id"] - 1
        is_house : bool = entry.get("type") is None
        
        if owner not in owners_info:
            owners_info[owner] = {
                "houses_count": 0,
                "houses_ids": [],
                "businesses_count": 0,
                "businesses_ids": []
            }

        if is_house:
            owners_info[owner]["houses_count"] += 1
            owners_info[owner]["houses_ids"].append(owner_id)
        else:
            owners_info[owner]["businesses_count"] += 1
            owners_info[owner]["businesses_ids"].append(owner_id)

    
    return owners_info


async def handle_payday_stats(request : PaydayStatPostRequest) -> None:
    last_payday_stat_optional : dict = await payday_stats_table.find_one({"server_name" : request.server_name.lower()}, sort=[("datetime", DESC)])
    
    payday_stat_schema : PaydayStatSchema = PaydayStatSchema(server_name=request.server_name.lower(), properties=request.properties, datetime=datetime.now(ZoneInfo("Europe/Moscow")), page_number=request.page_number)

    if last_payday_stat_optional is None:
        print("inserting")
        await payday_stats_table.insert_one(payday_stat_schema.model_dump(by_alias=True))
        return

    if await payday_stats_table.count_documents({"server_name" : request.server_name}) >= 20:
        print("deleting")
        await payday_stats_table.delete_one(
            {
                "_id" : (await payday_stats_table.find_one({"server_name" : request.server_name}, sort=[("datetime", ASC)])).get("_id")
            }
        )

    payday_stat_serialized : dict = payday_stat_schema.model_dump(by_alias=True)

    if not await payday_stats_table.find_one({"server_name" : payday_stat_serialized["server_name"], "properties" : payday_stat_serialized["properties"]}):
        print("inserting new")
        await payday_stats_table.insert_one(payday_stat_serialized)


async def payday_stats_by_server_name(request : PaydayStatGetByServerNameRequest) -> list[dict]:
    payday_stats : list[dict] = await payday_stats_table.find({"server_name" : request.server_name.lower()}).sort("datetime", DESC).to_list(length=None)
    for payday_stat in payday_stats:
        if payday_stat.get("datetime"):
            utc_datetime : datetime = payday_stat.get("datetime")

            moscow_time = utc_datetime.astimezone(ZoneInfo("Europe/Moscow"))
            payday_stat["datetime"] = moscow_time.strftime("%d-%m-%Y %H:%M:%S") + " MSK"
    return payday_stats



async def make_async_get_request(url : str, headers : dict = None, data : dict = None):
    if data:
        async with httpx.AsyncClient() as client:
            return await client.get(url, headers=headers, params=data)
    
    async with httpx.AsyncClient() as client:
        return await client.get(url, headers=headers)


# async def make_post_request(url : str, headers : dict = None, data : dict = None):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#         return response


