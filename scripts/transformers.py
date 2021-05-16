from dateutil.parser import parse
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Dict, List

from app_frenzy.db import SessionLocal
from app_frenzy.models import (
    Days,
    MenuItem,
    Restaurant,
    RestaurantTiming,
    User,
    UserTransaction,
)
from app_frenzy.schemas import (
    MenuItemSchema,
    RestaurantSchema,
    RestaurantTimingSchema,
    UserSchema,
    UserTransactionSchema,
)

import re


TIMING_RE = re.compile(
    "(?P<first>([a-zA-Z]+\s*,?-?\s*)*[a-zA-Z]+)\s*(?P<second>\d*:?\d+\s*[a-zA-Z]+\s*-\s*\d*:?\d+\s*[a-zA-Z]+)"
)
DAYS_MAP = {
    "mon": Days.mon,
    "tue": Days.tues,
    "wed": Days.weds,
    "thu": Days.thurs,
    "fri": Days.fri,
    "sat": Days.sat,
    "sun": Days.sun,
}


def make_model_obj(doc: dict, schema, model):
    return model(**schema(**doc).dict())


def find_days_enum_value(day: str):
    for _day, v in DAYS_MAP.items():
        if day.lower().startswith(_day):
            return v
    raise Exception("Day lookup failed in map for day: %s" % (day))


def extract_days_list(days: str):
    days = days.strip()
    if "-" in days:
        days_list = list(
            map(lambda x: find_days_enum_value(x.strip()), days.split("-"))
        )
        start = days_list[0].value
        end = start + (days_list[1].value - start + 7) % 7
        return [Days(i % 7) for i in range(start, end + 1)]
    elif "," in days:
        return list(
            map(lambda x: find_days_enum_value(x.strip()), days.split(","))
        )

    return [find_days_enum_value(days)]


def transform_into_restaurant_timing_objs(
    timings: str, restaurant: Restaurant
):
    objs = []
    for timing in timings.split("/"):
        matches = TIMING_RE.match(timing.strip())
        days = matches.group("first")
        time_band = matches.group("second")
        open_closes = time_band.split("-")

        opens = parse(open_closes[0]).time()
        closes = parse(open_closes[1]).time()
        days_list = extract_days_list(days)
        for day in days_list:
            doc = {
                "restaurant": restaurant.id,
                "day": day,
                "opens": opens,
                "closes": closes,
            }
            objs.append(
                make_model_obj(doc, RestaurantTimingSchema, RestaurantTiming)
            )
    return objs


def transform_into_menu_objs(menu_items: List[Dict], restaurant: Restaurant):
    objs = []
    for menu_item in menu_items:
        menu_item_obj = make_model_obj(menu_item, MenuItemSchema, MenuItem)
        menu_item_obj.restaurant = restaurant.id
        objs.append(menu_item_obj)
    return objs


def transform_into_restaurant_obj(restaurant: dict):
    return make_model_obj(restaurant, RestaurantSchema, Restaurant)


def get_restaurant_with_name(name: str, session: Session):
    query = select(Restaurant).filter_by(name=name)
    return session.execute(query).scalars().first()


def get_menu_item_with_dish_name(dish_name: str, session: Session):
    query = select(MenuItem).filter_by(dish_name=dish_name)
    return session.execute(query).scalars().first()


def transform_into_purchase_history_objs(
    purchase_history: List[Dict], user: User
):
    objs = []
    for purchase in purchase_history:
        with SessionLocal() as session:
            restaurant = get_restaurant_with_name(
                purchase["restaurantName"], session
            )
            menu_item = get_menu_item_with_dish_name(
                purchase["dishName"], session
            )
            doc = {
                "user": user.id,
                "restaurant": restaurant.id,
                "menu_item": menu_item.id,
                "transactionAmount": purchase["transactionAmount"],
                "transactionDate": parse(purchase["transactionDate"].strip()),
            }
            objs.append(
                make_model_obj(doc, UserTransactionSchema, UserTransaction)
            )
    return objs


def transform_into_user_obj(user: dict):
    return make_model_obj(user, UserSchema, User)
