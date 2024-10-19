from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class BuySchema(BaseModel):
    id : UUID = Field(alias="_id")
    buy_time : datetime
    user_id : str
    token : str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID : str,
            datetime : lambda v : v.isoformat()
        }


class ReportSchema(BaseModel):
    id : UUID = Field(alias="_id")
    user_id : int
    user_fullname : str
    message : str
    datetime : datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID : str,
            datetime : lambda v : v.isoformat()
        }
