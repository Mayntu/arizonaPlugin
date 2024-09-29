from fastapi import HTTPException
from random import randint
from datetime import datetime, timedelta, timezone
from math import ceil, floor
from redis import asyncio as aioredis

from src.database.dto.api_requests import (
    GetCaptchasRequest, ConvertTimeRequest, CheckServerRequest, CheckServerInServersRequest, CalcTaxRequest, SearchPropertyRequest
)
from src.database.dto.api_responses import (
    CalcTaxResponse
)
from src.database.settings import (
    MOSCOW_UTC_OFFSET,
    ARIZONA_SERVERS,
    ARIZONA_IP_LIST,
    ARIZONA_MAP_URL,
    PROPS
)

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
            local_time = datetime.fromtimestamp(seconds_since_epoch, tz=timezone.utc)
    
    if not request.isNumber:
        local_time : datetime = datetime.strptime(request.time, "%H:%M:%S")

    try:
        moscow_time = local_time - timedelta(hours=request.offset - MOSCOW_UTC_OFFSET)

        print(f"User time: {local_time}")
        print(f"UTC offset: {request.offset}")
        print(f"MOSCOW time: {moscow_time}")

        return moscow_time.strftime("%H:%M:%S")
    
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
    if request.calcInMskTime:
        tz : timezone = timezone(timedelta(hours=3))
        seconds_when_expire : int = time + seconds_remaining

    calc_tax_response : CalcTaxResponse = CalcTaxResponse(
        hours=hours,
        days=days,
        leftHours=leftHours,
        date=datetime.strftime(datetime.fromtimestamp(seconds_when_expire, tz=tz), format="%d.%m.%Y %H:00")
    )

    return calc_tax_response


async def search_property(request : SearchPropertyRequest, redis : aioredis.Redis) -> dict:
    arizona_map_headers : dict = {
        "accept" : "application/json",
        "origin" : "https://arizona-rp.com/",
        "referer" : "https://arizona-rp.com/",
    }
    cache_key = f"arizona_map_{request.serverNumber}"
    cached_data = await redis.get(cache_key)

    if cached_data:
        print("Данные взяты из кэша")
        map_data = json.loads(cached_data)
    else:
        response: httpx.Response = await make_get_request(
            headers=arizona_map_headers,
            url=ARIZONA_MAP_URL + f"/{request.serverNumber}"
        )

        if not response.status_code in range(190, 230):
            raise HTTPException(status_code=500, detail="arizona map api not working")
        
        map_data: dict = response.json()

        # Кэшируем данные на 10 минут (600 секунд)
        await redis.setex(cache_key, 600, json.dumps(map_data))


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



async def make_get_request(url : str, headers : dict = None, data : dict = None):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=data)
        return response


# async def make_post_request(url : str, headers : dict = None, data : dict = None):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, headers=headers, json=data)
#         return response


