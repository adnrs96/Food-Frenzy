from app_frenzy.models import Days
from datetime import datetime, time
from pydantic import BaseModel, Field, validator, ValidationError
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


class RestaurantFilterQueryParamsSchema(BaseModel):
    open_at: Optional[datetime]
    price_lower: Optional[float]
    price_upper: Optional[float]

    @validator("open_at", pre=True)
    def validate_transform_open_at(cls, value):
        if isinstance(value, datetime) or value is None:
            return value
        try:
            dt = datetime.utcfromtimestamp(value)
        except Exception:
            raise ValidationError("Invalid timestampt format: open_at")
        return dt


class ListRestaurantResponseSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
