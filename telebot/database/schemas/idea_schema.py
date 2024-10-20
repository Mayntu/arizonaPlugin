from pydantic import BaseModel, Field
from bson import ObjectId
from datetime import datetime

class IdeaSchema(BaseModel):
    id : ObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id : int
    user_fullname : str
    user_login : str
    message : str
    datetime : datetime
    is_active : bool = True

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId : str,
            datetime : lambda v : v.isoformat()
        }
