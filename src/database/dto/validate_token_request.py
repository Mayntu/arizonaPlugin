from pydantic import BaseModel


class ValidateTokenRequest(BaseModel):
    hwid : str