from fastapi import APIRouter, Body, BackgroundTasks, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from redis import asyncio as aioredis

from src.database.schemas.payday_stats_schema import PaydayStatSchema

from src.database.dto.api_requests import (
    ValidateTokenRequest,
    GetCaptchasRequest,
    ConvertTimeRequest,
    CheckServerRequest,
    CheckServerInServersRequest,
    CalcTaxRequest,
    SearchPropertyRequest,
    PaydayStatPostRequest,
    PaydayStatGetByServerNumberRequest
)
from src.database.dto.api_responses import (
    CalcTaxResponse,
    ExpireTimeResponse
)

from src.services.token_service import(
    create_token,
    validate_token,
    validate_pass,
    get_expire_time
)
from src.services.captcha_service import (
    get_captchas,
    convert_local_time_to_moscow,
    check_server_is_in_list,
    check_server_is_in_servers,
    calc_tax,
    search_property,
    handle_payday_stats,
    payday_stats_by_server_name
)

from src.database.redis_client import redis_client


api_router : APIRouter = APIRouter()



@api_router.get("/check")
def check():
    return 200


@api_router.post("/token", response_model=dict[str, str])
async def api_create_token(data = Body()) -> dict[str, str]:
    try:
        key : str = data.get("secret")
        result : bool = validate_pass(key=key)
        if not result:
            return JSONResponse(content={"message" : "not correct key"}, status_code=400)
        
        token_id : str = await create_token()
        return JSONResponse(content={"token_id" : token_id}, status_code=201)
    except HTTPException as e:
        return JSONResponse(content={"message" : str(e)}, status_code=e.status_code)
    except AttributeError as e:
        return JSONResponse(content={"message" : "not correct data"}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message" : f"internal server error {e}"}, status_code=500)


@api_router.post("/token/{token_id}/validate")
async def api_is_token_valid(token_id : str, request : ValidateTokenRequest):
    hwid : str = request.hwid
    is_valid : bool = await validate_token(token_id, hwid)
    return JSONResponse(content={"is_valid" : is_valid}, status_code=200)


@api_router.post("/get_captchas/{token_id}")
async def api_get_captchas(token_id : str, request : GetCaptchasRequest):
    hwid : str = request.hwid
    await validate_token(token_id, hwid)
    captchas : list[str] = await get_captchas(request)
    return JSONResponse(content={"captchas" : captchas}, status_code=200)


@api_router.post("/convert_time_to_moscow/{token_id}")
async def api_convert_time_to_moscow(token_id : str, request : ConvertTimeRequest):
    hwid : str = request.hwid
    await validate_token(token_id, hwid)
    
    try:
        time : str | int = await convert_local_time_to_moscow(
            request=request
        )
        return JSONResponse(content={"time" : time}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"messsage" : e.detail}, status_code=e.status_code)


@api_router.post("/check_server/{token_id}")
async def api_check_server_in_list(token_id : str, request : CheckServerRequest):
    hwid : str = request.hwid
    await validate_token(token_id, hwid)
    
    try:
        is_in_list : bool = await check_server_is_in_list(
            request=request
        )
        return JSONResponse(content={"is_in_list" : is_in_list}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"messsage" : e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"message" : f"internal server error : {e}"}, status_code=500)


@api_router.post("/check_server_in_servers/{token_id}")
async def api_check_server_in_servers(token_id : str, request : CheckServerInServersRequest):
    hwid : str = request.hwid
    await validate_token(token_id, hwid)
    
    try:
        is_in_servers : bool = await check_server_is_in_servers(
            request=request
        )
        return JSONResponse(content={"is_in_list" : is_in_servers}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"messsage" : e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"message" : f"internal server error : {e}"}, status_code=500)


@api_router.post("/calc_tax/{token_id}", response_model=CalcTaxResponse, status_code=200)
async def api_calc_tax(token_id : str, request : CalcTaxRequest):
    hwid : str = request.hwid
    await validate_token(token_id, hwid)
    
    try:
        calc_tax_response : CalcTaxResponse = await calc_tax(
            request=request
        )
        return calc_tax_response
    except HTTPException as e:
        return JSONResponse(content={"messsage" : e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"message" : f"internal server error : {e}"}, status_code=500)


@api_router.post("/search_property/{token_id}")
async def api_search_property(token_id : str, request : SearchPropertyRequest, redis : aioredis.Redis = Depends(lambda: redis_client.redis)):
    hwid : str = request.hwid
    await validate_token(token_id, hwid)

    try:
        response : dict = await search_property(
            request=request,
            redis=redis
        )
        return JSONResponse(content={"result" : response}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"message" : e.detail}, status_code=e.status_code)
    except Exception as e:
        print("internal server error : " + {e})
        return JSONResponse(content={"message" : f"internal server error : {e}"}, status_code=500)


@api_router.post("/token/get_expire_time/{token_id}", response_model=ExpireTimeResponse, status_code=200)
async def api_get_expire_time(token_id : str, request : ValidateTokenRequest) -> ExpireTimeResponse:
    hwid : str = request.hwid
    await validate_token(token_id, hwid)

    return await get_expire_time(token_id)


@api_router.post("/payday_stats/{token_id}", status_code=201)
async def post_payday_stats(token_id : str, request : PaydayStatPostRequest, background_tasks : BackgroundTasks) -> None:
    hwid : str = request.hwid
    await validate_token(token_id=token_id, hwid=hwid)

    background_tasks.add_task(handle_payday_stats, request)


@api_router.post("/payday_stats/{token_id}/server", response_model=list[PaydayStatSchema], status_code=200)
async def get_payday_stats(token_id : str, request : PaydayStatGetByServerNumberRequest) -> list[PaydayStatSchema]:
    hwid : str = request.hwid
    await validate_token(token_id=token_id, hwid=hwid)

    return await payday_stats_by_server_name(request=request)
