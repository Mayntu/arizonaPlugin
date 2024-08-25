from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class BuySchema(BaseModel):
    id : UUID = Field(alias="_id")
    buy_time : datetime
    user_id : str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID : str,
            datetime : lambda v : v.isoformat()
        }
