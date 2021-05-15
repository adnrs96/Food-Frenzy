#!/usr/bin/python3
from typing import Dict, List
import os
import sys

APP_FRENZY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(APP_FRENZY_PATH)

from app_frenzy.db import SessionLocal
from app_frenzy.models import Restaurant
from scripts.transformers import (
    transform_into_menu_objs,
    transform_into_restaurant_obj,
)
from sqlalchemy.orm import Session

import json
import requests


RESTAURANT_DATA_URI = "https://gist.githubusercontent.com/seahyc/b9ebbe264f8633a1bf167cc6a90d4b57/raw/021d2e0d2c56217bad524119d1c31419b2938505/restaurant_with_menu.json"
USER_DATA_URI = "https://gist.githubusercontent.com/seahyc/de33162db680c3d595e955752178d57d/raw/785007bc91c543f847b87d705499e86e16961379/users_with_purchase_history.json"

DATA_PATH = os.path.join(APP_FRENZY_PATH, "data")
RESTAURANT_FILE_PATH = os.path.join(DATA_PATH, "restaurant_db.json")
USER_FILE_PATH = os.path.join(DATA_PATH, "user.json")


def create_data_dir_if_not_exists():
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)


def fetch_and_save(url: str, path: str):
    with open(path, "w") as f:
        resp = requests.get(url)
        f.write(resp.text)


def read_json(file_path: str):
    with open(file_path, "r") as f:
        return json.loads(f.read())


def generate_field_map_from_list_dict(lst: List[Dict], dict_field_name: str):
    mapping = {}
    for ele in lst:
        mapping[ele[dict_field_name]] = ele
    return mapping


def populate_menu_items(
    menu_items: List[Dict], restaurant: Restaurant, session: Session
):
    menu_item_objs = transform_into_menu_objs(menu_items, restaurant)
    session.add_all(menu_item_objs)
    session.flush()


def _populate_restaurants(restaurants: Dict[str, Dict], session: Session):
    for _, restaurant in restaurants.items():
        restaurant_obj = transform_into_restaurant_obj(restaurant)
        session.add(restaurant_obj)
        session.flush()

        populate_menu_items(restaurant["menu"], restaurant_obj, session)


def populate_restaurants(file_path: str):
    restaurants = read_json(file_path)
    restaurant_map = generate_field_map_from_list_dict(
        restaurants, "restaurantName"
    )
    with SessionLocal() as session:
        _populate_restaurants(restaurant_map, session)
        session.commit()


if __name__ == "__main__":
    create_data_dir_if_not_exists()

    fetch_and_save(RESTAURANT_DATA_URI, RESTAURANT_FILE_PATH)
    fetch_and_save(USER_DATA_URI, USER_FILE_PATH)
    populate_restaurants(RESTAURANT_FILE_PATH)
