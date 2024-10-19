from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

class ReportSchema(BaseModel):
    id : ObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id : int
    user_fullname : str
    user_login : str
    message : str
    datetime : datetime

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId : str,
            datetime : lambda v : v.isoformat()
        }
