from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(from_attributes=True)
