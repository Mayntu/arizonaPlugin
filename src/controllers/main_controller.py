from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from src.database.schemas.token_schema import TokenSchema

from src.database.dto.activate_token_request import (
    ActivateTokenRequest
)

from src.services.token_service import(
    create_token,
    activate_token
)


api_router : APIRouter = APIRouter()


@api_router.post("/token",response_model=dict[str, str])
async def add_product_to_cart() -> dict[str, str]:
    try:
        token_id : str = await create_token()
        return JSONResponse(content={"token_id" : token_id}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message" : f"internal server error {e}"}, status_code=500)


@api_router.post("/token/{token_id}/activate")
async def add_product_to_cart(token_id : str, request : ActivateTokenRequest):
    hwid : str = request.hwid
    try:
        await activate_token(token_id, hwid)
        return JSONResponse(content={"message" : "token was activated"}, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"message" : e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"message" : f"internal server error is {e}"}, status_code=500)
