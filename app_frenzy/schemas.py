from app_frenzy.models import Days
from datetime import time
from pydantic import BaseModel, Field
from typing import Optional


class RestaurantSchema(BaseModel):
    name: str = Field(alias="restaurantName")
    cash_balance: float = Field(alias="cashBalance")


class MenuItemSchema(BaseModel):
    restaurant: Optional[int]
    dish_name: str = Field(alias="dishName")
    price: float


class RestaurantTimingSchema(BaseModel):
    restaurant: Optional[int]
    day: Days
    opens: time
    closes: time
