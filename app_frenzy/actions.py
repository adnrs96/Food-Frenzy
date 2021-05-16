from datetime import datetime, timezone
from typing import List

from app_frenzy.models import Days, MenuItem, Restaurant, RestaurantTiming
from app_frenzy.schemas import RestaurantFilterQueryParamsSchema
from app_frenzy.db import SessionLocal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

import enum


class RestaurantFilterEnum(enum.Enum):
    OPEN_AT = "open_at"
    PRICE = "price"


class RestaurantFilter:
    FILTERS = list(map(lambda x: x.value, list(RestaurantFilterEnum)))

    def __init__(self, filters, open_at, price_lower, price_upper):
        self.filters = filters
        # Parse and transform query params to required form.
        # Raises Error on failure.
        query_params = RestaurantFilterQueryParamsSchema(
            open_at=open_at,
            price_lower=price_lower,
            price_upper=price_upper,
        ).dict()
        self.open_at = query_params["open_at"]
        self.price_lower = query_params["price_lower"]
        self.price_upper = query_params["price_upper"]

        self.validate_filter_params()
        self.optimise_filters()
        if self.add_default_filter():
            # By default if no filters are specified we apply
            # RestaurantFilterEnum.OPEN_AT
            self.filters.append(RestaurantFilterEnum.OPEN_AT)

    @staticmethod
    def validate_filters(filters: List[str]):
        if len(filters) > len(RestaurantFilter.FILTERS):
            return False
        for filter_type in filters:
            if filter_type not in RestaurantFilter.FILTERS:
                return False
        return True

    def validate_filter_params(self):
        if (
            self.price_lower is None
            and self.price_upper is None
            and RestaurantFilterEnum.PRICE.value in self.filters
        ):
            raise HTTPException(
                status_code=422,
                detail="Filter price requires at least one of price_lower or price_upper.",
            )

    def optimise_filters(self):
        # In this function we will be removing the filters
        # which are useless since they don't really filter on anything.

        # Remove multiple instances of same filter.
        self.filters = list(set(self.filters))

    def add_default_filter(self):
        if not self.filters:
            return True
        return False

    def apply_filter_open_at(self, query, open_at: datetime):
        day = Days(open_at.weekday())
        open_at_time = open_at.time()
        query = query.join(Restaurant.timings).filter(
            RestaurantTiming.day == day,
            RestaurantTiming.opens < open_at_time,
            RestaurantTiming.closes > open_at_time,
        )
        return query

    def apply_filter_price(self, query, price_lower, price_upper):
        query = query.join(Restaurant.menu)
        if price_lower:
            query = query.filter(MenuItem.price >= price_lower)
        if price_upper:
            query = query.filter(MenuItem.price <= price_upper)
        return query

    def get_filtered_restaurants(self):
        with SessionLocal() as session:
            query = select(Restaurant)
            for filter_type in self.filters:
                if filter_type == RestaurantFilterEnum.OPEN_AT.value:
                    open_at = (
                        self.open_at if self.open_at else datetime.utcnow()
                    )
                    query = self.apply_filter_open_at(query, self.open_at)
                elif filter_type == RestaurantFilterEnum.PRICE.value:
                    query = self.apply_filter_price(
                        query, self.price_lower, self.price_upper
                    )
            return session.execute(query).scalars().all()


class GenerateResponse:
    def __init__(self, results, schema):
        self.results = results
        self.schema = schema

    def apply_schema(self, doc):
        return self.schema.from_orm(doc).dict(exclude_none=True)

    def generate(self):
        if isinstance(self.results, list):
            return list(map(self.apply_schema, self.results))
        return self.apply_schema(self.results)
