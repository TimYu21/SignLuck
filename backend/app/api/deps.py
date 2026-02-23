from functools import lru_cache

from app.core.repository import CountryRepository
from app.services.calculator import PlateCalculator
from app.services.plate_service import PlateService


@lru_cache
def get_country_repository() -> CountryRepository:
    """Возвращает экземпляр репозитория стран."""
    return CountryRepository()


@lru_cache
def get_plate_calculator() -> PlateCalculator:
    """Возвращает экземпляр калькулятора."""
    return PlateCalculator()


@lru_cache
def get_plate_service() -> PlateService:
    """Собирает PlateService со всеми зависимостями."""
    return PlateService(
        repository=get_country_repository(),
        calculator=get_plate_calculator(),
    )
