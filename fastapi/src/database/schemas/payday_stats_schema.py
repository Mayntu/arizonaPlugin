from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime


class PaydayStatSchema(BaseModel):
    id : UUID = Field(default_factory=uuid4, alias="_id")
    server_number : int
    properties : list["Property"]
    datetime : datetime
    
    class Property(BaseModel):
        id : int
        payday_count : int

        def equals(self, other : "Property") -> bool:
            return self.id == other.id and self.payday_count == other.payday_count


    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID : str,
            datetime : lambda v : v.isoformat()
        }

    def can_overwrite(self, other : "PaydayStatSchema") -> bool:
        len_self_properties : int = len(self.properties)
        if not len_self_properties == len(other.properties):
            return True
        
        for i in range(0, len_self_properties):
            if not self.properties[i].equals(other.properties[i]):
                return True
        
        return False
