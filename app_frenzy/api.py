from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from app_frenzy.actions import RestaurantFilter, GenerateResponse
from app_frenzy.schemas import ListRestaurantResponseSchema


router = APIRouter()


@router.get("/restaurant")
async def list_restaurant(
    filter_types: List[str] = Query(..., alias="filter"),
    open_at: Optional[int] = Query(None),
):
    if not RestaurantFilter.validate_filters(filter_types):
        raise HTTPException(status_code=422, detail="Invalid filters.")
    try:
        restaurant_filter = RestaurantFilter(filter_types, open_at)
        restaurants = restaurant_filter.get_filtered_restaurants()
        results = GenerateResponse(
            restaurants, ListRestaurantResponseSchema
        ).generate()
    except ValidationError:
        raise HTTPException(
            status_code=422, detail="Invalid filters or query params."
        )
    return {"status": "success", "restaurants": results}
