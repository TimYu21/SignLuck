from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CountrySchema(BaseModel):
    """
    Схема представления информации о стране и формате её автомобильных номеров.

    Используется для валидации данных из CSV-репозитория.

    Attributes:
        country_code (str): Двухбуквенный ISO-код страны.
        country_name (str): Полное название страны.
        pattern (str): Шаблон номерного знака.
        allowed_letters (str): Разрешённые буквы.
        lat (float): Географическая широта страны.
        lng (float): Географическая долгота страны.
    """

    country_code: str = Field(..., min_length=2, max_length=2)
    country_name: str
    country_name_en: Optional[str] = None
    pattern: str
    allowed_letters: str = ""
    lat: float
    lng: float
    flag_emoji: Optional[str] = None

    @field_validator("country_code")
    @classmethod
    def normalize_country_code(cls, v: str) -> str:
        return v.upper()

    class Config:
        from_attributes = True


class PlateVisualSymbol(BaseModel):
    """Один символ номерного знака для визуализации."""

    value: str
    is_fixed: bool
    possible_query_indices: List[int] = Field(default_factory=list)


class PlateExampleSymbol(BaseModel):
    """Символ в сгенерированном примере номера."""

    value: str
    is_query: bool  # Является ли этот символ частью искомой комбинации


class PlateCalculationResult(BaseModel):
    """Результат расчета вероятности для конкретной страны."""

    country_name: str
    country_code: str
    lat: float
    lng: float
    probability: float = Field(..., ge=0.0, le=100.0)
    symbols: List[PlateVisualSymbol]
    allowed_letters: str
    pattern: str
    flag_emoji: Optional[str] = None
    examples: List[List[PlateExampleSymbol]] = Field(default_factory=list)


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
