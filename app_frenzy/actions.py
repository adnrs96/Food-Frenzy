from datetime import datetime, timezone
from typing import List

from app_frenzy.models import Days, Restaurant, RestaurantTiming
from app_frenzy.schemas import RestaurantFilterQueryParamsSchema
from app_frenzy.db import SessionLocal

from sqlalchemy import select
from sqlalchemy.orm import Session

import enum


class RestaurantFilterEnum(enum.Enum):
    OPEN_AT = "open_at"


class RestaurantFilter:
    FILTERS = list(map(lambda x: x.value, list(RestaurantFilterEnum)))

    def __init__(self, filters, open_at):
        self.filters = filters
        if not self.filters:
            # By default if no filters are specified we apply
            # RestaurantFilterEnum.OPEN_AT
            self.filters.append(RestaurantFilterEnum.OPEN_AT)
        # Parse and transform query params to required form.
        # Raises Error on failure.
        query_params = RestaurantFilterQueryParamsSchema(
            open_at=open_at
        ).dict()
        self.open_at = query_params["open_at"]

    @staticmethod
    def validate_filters(filters: List[str]):
        if len(filters) > len(RestaurantFilter.FILTERS):
            return False
        for filter_type in filters:
            if filter_type not in RestaurantFilter.FILTERS:
                return False
        return True

    def apply_filter_open_at(self, query, open_at: datetime):
        day = Days(open_at.weekday())
        open_at_time = open_at.time()
        query = query.join(Restaurant.timings).filter(
            RestaurantTiming.day == day,
            RestaurantTiming.opens < open_at_time,
            RestaurantTiming.closes > open_at_time,
        )
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
