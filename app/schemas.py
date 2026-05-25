from pydantic import BaseModel, ConfigDict
from datetime import date, datetime


class FoodCreate(BaseModel):
    name: str
    quantity: int = 1
    expiration_date: date

class FoodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    quantity: int
    expiration_date: date
    added_at: datetime
    
class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    data: dict
    created_at: datetime