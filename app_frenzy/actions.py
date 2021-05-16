from datetime import datetime, timezone
from typing import List

from app_frenzy.models import Days, MenuItem, Restaurant, RestaurantTiming
from app_frenzy.schemas import RestaurantFilterQueryParamsSchema
from app_frenzy.db import SessionLocal

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

import enum


class RestaurantFilterEnum(enum.Enum):
    OPEN_AT = "open_at"
    PRICE = "price"
    NDISH = "ndish"


class RestaurantFilter:
    FILTERS = list(map(lambda x: x.value, list(RestaurantFilterEnum)))

    def __init__(
        self, filters, open_at, price_lower, price_upper, ndish_gt, ndish_lt
    ):
        self.filters = filters
        # Parse and transform query params to required form.
        # Raises Error on failure.
        query_params = RestaurantFilterQueryParamsSchema(
            open_at=open_at,
            price_lower=price_lower,
            price_upper=price_upper,
            ndish_gt=ndish_gt,
            ndish_lt=ndish_lt,
        ).dict()
        self.open_at = query_params["open_at"]
        self.price_lower = query_params["price_lower"]
        self.price_upper = query_params["price_upper"]
        self.ndish_gt = query_params["ndish_gt"]
        self.ndish_lt = query_params["ndish_lt"]

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
        if (
            self.ndish_gt is None
            and self.ndish_lt is None
            and RestaurantFilterEnum.NDISH.value in self.filters
        ):
            raise HTTPException(
                status_code=422,
                detail="Filter ndish requires at least one of ndish_gt or ndish_lt.",
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

    def apply_filter_open_at(self, query, joins, open_at: datetime):
        day = Days(open_at.weekday())
        open_at_time = open_at.time()
        if "timings" not in joins:
            joins["timings"] = 1
            query = query.join(Restaurant.timings)
        query = query.filter(
            RestaurantTiming.day == day,
            RestaurantTiming.opens < open_at_time,
            RestaurantTiming.closes > open_at_time,
        )
        return query

    def apply_filter_price(self, query, joins, price_lower, price_upper):
        if "menu" not in joins:
            joins["menu"] = 1
            query = query.join(Restaurant.menu)
        if price_lower:
            query = query.filter(MenuItem.price >= price_lower)
        if price_upper:
            query = query.filter(MenuItem.price <= price_upper)
        return query

    def apply_filter_ndish(
        self,
        query,
        joins,
        ndish_gt,
        ndish_lt,
    ):
        # Preferance is given to greater than if both the
        # operations are present in the request and we allow
        # it to flow to db.
        if "menu" not in joins:
            joins["menu"] = 1
            query = query.join(Restaurant.menu)
        if ndish_gt:
            query = query.group_by(Restaurant.id).having(
                func.count(Restaurant.menu) > ndish_gt
            )
        elif ndish_lt:
            query = query.group_by(Restaurant.id).having(
                func.count(Restaurant.menu) < ndish_lt
            )
        return query

    def get_filtered_restaurants(self):
        with SessionLocal() as session:
            query = select(Restaurant)
            # This dict is mutated by downstream filter funcs
            joins = {}
            for filter_type in self.filters:
                if filter_type == RestaurantFilterEnum.OPEN_AT.value:
                    open_at = (
                        self.open_at if self.open_at else datetime.utcnow()
                    )
                    query = self.apply_filter_open_at(query, joins, open_at)
                elif filter_type == RestaurantFilterEnum.PRICE.value:
                    query = self.apply_filter_price(
                        query, joins, self.price_lower, self.price_upper
                    )
                elif filter_type == RestaurantFilterEnum.NDISH.value:
                    query = self.apply_filter_ndish(
                        query, joins, self.ndish_gt, self.ndish_lt
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
