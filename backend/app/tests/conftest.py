import pytest
from app.main import app
from app.schemas.country import CountrySchema
from app.services.calculator import PlateCalculator
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Фикстура клиента API для интеграционных тестов."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def calculator():
    """Фикстура экземпляра калькулятора."""
    return PlateCalculator()


@pytest.fixture
def sample_country_ru():
    """Пример сложного шаблона (Россия)."""
    return CountrySchema(
        country_code="RU",
        country_name="Russia",
        pattern="A 000 AA",
        allowed_letters="ABEKMHOPCTYX",
        lat=55.75,
        lng=37.61,
        flag_emoji="🇷🇺",
    )


@pytest.fixture
def sample_country_simple():
    """Пример простого шаблона для математических проверок."""
    # Шаблон: 3 буквы. Разрешены: A, B, C.
    # Всего вариантов: 3 * 3 * 3 = 27.
    return CountrySchema(
        country_code="XX",
        country_name="TestLand",
        pattern="AAA",
        allowed_letters="ABC",
        lat=0.0,
        lng=0.0,
    )
