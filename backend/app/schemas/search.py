from typing import List, Optional

from app.schemas.plate import PlateCalculationResult
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """Схема входящего запроса."""

    query: str = Field(..., min_length=1, max_length=10)
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None

    @field_validator("query")
    @classmethod
    def normalize_query(cls, v: str) -> str:
        return v.strip().upper()


class SearchResponse(BaseModel):
    """Схема ответа на поисковый запрос."""

    results: List[PlateCalculationResult]
    total_results: int
    max_probability: float
    suggestions: List[str] = Field(default_factory=list)
