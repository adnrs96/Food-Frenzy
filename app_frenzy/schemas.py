from pydantic import BaseModel, Field


class RestaurantSchema(BaseModel):
    name: str = Field(alias="restaurantName")
    cash_balance: float = Field(alias="cashBalance")


class MenuItemSchema(BaseModel):
    dish_name: str = Field(alias="dishName")
    price: float
