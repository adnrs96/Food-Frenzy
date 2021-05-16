from app_frenzy.models import Days
from datetime import datetime, time
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


class UserSchema(BaseModel):
    str_id: str = Field(alias="id")
    name: str
    cash_balance: float = Field(alias="cashBalance")


class UserTransactionSchema(BaseModel):
    user: Optional[int]
    restaurant: Optional[int]
    menu_item: Optional[int]
    transaction_amount: float = Field(alias="transactionAmount")
    transaction_date: datetime = Field(alias="transactionDate")
