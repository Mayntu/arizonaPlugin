from pydantic import BaseModel

class CalcTaxResponse(BaseModel):
    hours : int
    days : int
    leftHours : int
    date : str