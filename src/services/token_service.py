from uuid import UUID
from fastapi import HTTPException
from datetime import datetime, timezone
from hmac import new as hmac_new, HMAC
from hashlib import sha256

from src.database.settings import tokens_table, TOKEN_PASS_HASH, CRYPT_KEY
from src.database.schemas.token_schema import TokenSchema



async def create_token() -> str:
    token_schema : TokenSchema = TokenSchema(
        is_activated=False,
        hwid=None,
        created_time=datetime.now(timezone.utc),
        live_time=60
    )
    token_inserted = await tokens_table.insert_one(token_schema.model_dump(by_alias=True))
    token_id : str = str(token_inserted.inserted_id)
    return token_id


async def validate_token(token_id : str, hwid : str) -> bool:
    try:
        token = await tokens_table.find_one({
                "_id" : UUID(token_id),
        })
    except Exception as e:
        raise HTTPException(status_code=404, detail="not correct id")
    
    if token:
        token_schema : TokenSchema = TokenSchema(**token)
        if token_schema.is_activated:
            if token_schema.is_expired():
                raise HTTPException(status_code=400, detail="token expired")
            
            return hwid == token_schema.hwid

        updated_result = await tokens_table.update_one(
            {"_id": UUID(token_id)},
            {"$set": {"is_activated": True, "hwid": hwid}}
        )

        if updated_result.modified_count == 0:
            raise HTTPException(status_code=400, detail="not correct data")
        
        return True
    
    raise HTTPException(status_code=404, detail="token not found")


def validate_pass(key : str) -> bool:
    if not key:
        raise HTTPException(status_code=400, detail="not correct key")
    
    key_hash : str = get_hash(text=key, secret_key=CRYPT_KEY)
    
    if str(key_hash) == str(TOKEN_PASS_HASH):
        return True
    
    raise HTTPException(status_code=400, detail="not correct key")


def get_hash(text : str, secret_key : str) -> str:
    password_bytes = text.encode('utf-8')
    secret_key_bytes = secret_key.encode('utf-8')

    hmac_obj : HMAC = hmac_new(secret_key_bytes, password_bytes, sha256)

    return hmac_obj.hexdigest()

