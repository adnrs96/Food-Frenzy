from app_frenzy.db import AppFrenzyBase

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Index

import enum


class Days(enum.Enum):
    mon = 0
    tues = 1
    weds = 2
    thurs = 3
    fri = 4
    sat = 5
    sun = 6


class Restaurant(AppFrenzyBase):
    __tablename__ = "restaurant"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    cash_balance = Column(Float)
    menu = relationship("MenuItem")
    timings = relationship("RestaurantTiming")


class MenuItem(AppFrenzyBase):
    __tablename__ = "menu_item"
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey("restaurant.id"))
    dish_name = Column(String)
    price = Column(Float, index=True)


class RestaurantTiming(AppFrenzyBase):
    __tablename__ = "restaurant_timing"
    __table_args__ = (
        Index("restaurant_timing_idx", "day", "opens", "closes"),
    )
    id = Column(Integer, primary_key=True)
    restaurant = Column(Integer, ForeignKey("restaurant.id"))
    day = Column(Enum(Days))
    opens = Column(Time)
    closes = Column(Time)


class User(AppFrenzyBase):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    str_id = Column(String, index=True)
    name = Column(String)
    cash_balance = Column(Float)
    purchase_history = relationship("UserTransaction")


class UserTransaction(AppFrenzyBase):
    __tablename__ = "user_transactions"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("user.id"))
    restaurant = Column(Integer, ForeignKey("restaurant.id"))
    menu_item = Column(Integer, ForeignKey("menu_item.id"))
    transaction_amount = Column(Float)
    transaction_date = Column(DateTime)
