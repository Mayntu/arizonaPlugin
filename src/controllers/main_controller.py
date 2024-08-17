from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse

from src.database.schemas.token_schema import TokenSchema

from src.database.dto.validate_token_request import (
    ValidateTokenRequest
)

from src.services.token_service import(
    create_token,
    validate_token
)


api_router : APIRouter = APIRouter()


@api_router.post("/token",response_model=dict[str, str])
async def api_create_token() -> dict[str, str]:
    try:
        token_id : str = await create_token()
        return JSONResponse(content={"token_id" : token_id}, status_code=201)
    except Exception as e:
        return JSONResponse(content={"message" : f"internal server error {e}"}, status_code=500)


@api_router.post("/token/{token_id}/validate")
async def api_is_token_valid(token_id : str, request : ValidateTokenRequest):
    hwid : str = request.hwid
    is_valid : bool = await validate_token(token_id, hwid)
    return JSONResponse(content={"is_valid" : is_valid}, status_code=200)
