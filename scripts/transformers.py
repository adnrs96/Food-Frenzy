from typing import Dict, List

from app_frenzy.models import MenuItem, Restaurant, RestaurantTiming
from app_frenzy.schemas import (
    MenuItemSchema,
    RestaurantSchema,
    RestaurantTimingSchema,
)


def make_model_obj(doc: dict, schema, model):
    return model(**schema(**doc).dict())


def transform_into_menu_objs(menu_items: List[Dict], restaurant: Restaurant):
    objs = []
    for menu_item in menu_items:
        menu_item_obj = make_model_obj(menu_item, MenuItemSchema, MenuItem)
        menu_item_obj.restaurant = restaurant.id
        objs.append(menu_item_obj)
    return objs


def transform_into_restaurant_obj(restaurant: dict):
    return make_model_obj(restaurant, RestaurantSchema, Restaurant)
