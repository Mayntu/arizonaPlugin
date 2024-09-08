from pydantic import BaseModel

class CalcTaxResponse(BaseModel):
    resultRemain : str
    resultDate : str