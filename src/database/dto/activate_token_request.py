from pydantic import BaseModel


class ActivateTokenRequest(BaseModel):
    hwid : str