from src.database.settings import tokens_table
from src.database.schemas.token_schema import TokenSchema
from bson.objectid import ObjectId
from fastapi import HTTPException



async def create_token() -> str:
    token_inserted = await tokens_table.insert_one({
            "is_activated" : False,
            "hwid" : False
    })
    token_id : str = str(token_inserted.inserted_id)
    return token_id


async def activate_token(token_id : str, hwid : str) -> None:
    token = await tokens_table.find_one({
            "_id" : ObjectId(token_id),
    })
    if token:
        if not token["is_activated"]:
            updated_result = await tokens_table.update_one(
                {"_id": ObjectId(token_id)},
                {"$set": {"is_activated": True, "hwid": hwid}}
            )
            if updated_result.modified_count == 0:
                raise HTTPException(status_code=400, detail="not correct data")
        else:
            raise HTTPException(status_code=400, detail="token already activated")
    else:
        raise HTTPException(status_code=404, detail="token not found")
