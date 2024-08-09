from pydantic import BaseModel

class TokenSchema(BaseModel):
    is_activated : bool
    hwid : str