from typing import List, Optional

from pydantic import BaseModel, Field


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
