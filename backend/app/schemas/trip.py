from typing import List

from pydantic import BaseModel


class TripSegment(BaseModel):
    """Сегмент маршрута (перелет в конкретную страну)."""

    country_name: str
    country_code: str
    probability: float
    booking_url: str
    lat: float
    lng: float


class TripRouteResponse(BaseModel):
    """Ответ с построенным маршрутом путешествия."""

    segments: List[TripSegment]
