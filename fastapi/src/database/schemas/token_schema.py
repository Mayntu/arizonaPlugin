from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

class TokenSchema(BaseModel):
    id : UUID = Field(default_factory=uuid4, alias="_id")
    is_activated : bool
    hwid : str | None
    created_time : datetime
    live_time : int # seconds

    def get_expire_time(self) -> datetime:
        return self.created_time + timedelta(seconds=self.live_time)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.get_expire_time()
    
    def is_valid(self) -> bool:
        return self.is_expired()
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID : str,
            datetime : lambda v : v.isoformat()
        }
