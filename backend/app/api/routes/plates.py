from typing import List

from app.api.deps import get_plate_service
from app.schemas.country import CountrySchema
from app.schemas.search import SearchRequest, SearchResponse
from app.schemas.trip import TripRouteResponse
from app.services.plate_service import PlateService
from fastapi import APIRouter, Depends

router = APIRouter(prefix="", tags=["Plates"])


@router.get(
    "/countries",
    response_model=List[CountrySchema],
    summary="Получить список всех стран",
    description="Возвращает полный список поддерживаемых стран с шаблонами номерных знаков.",
)
async def list_countries(
    service: PlateService = Depends(get_plate_service),
):
    """HTTP-обработчик списка стран."""
    return service.repository.get_all()


@router.post(
    "/check",
    response_model=SearchResponse,
    summary="Проверить комбинацию номерного знака",
    description=(
        "Вычисляет вероятность вхождения комбинации "
        "в номера всех поддерживаемых стран."
    ),
)
async def check_plate(
    request: SearchRequest,
    lang: str = "ru",
    service: PlateService = Depends(get_plate_service),
):
    """HTTP-обработчик проверки комбинации."""
    results = service.check_plate(request.query, lang)

    if not results:
        return SearchResponse(results=[], total_results=0, max_probability=0.0)

    # Статистика теперь тоже вычисляется на бэкенде
    max_prob = max(r.probability for r in results) if results else 0.0

    return SearchResponse(
        results=results,
        total_results=len(results),
        max_probability=max_prob,
    )


@router.post(
    "/route",
    response_model=TripRouteResponse,
    summary="Построить маршрут удачи по результатам комбинации",
    description="Строит маршрут путешествия по странам с наибольшей вероятностью встречи номера.",
)
async def build_route(
    request: SearchRequest,
    lang: str = "ru",
    service: PlateService = Depends(get_plate_service),
):
    """Генерация маршрута со ссылками на билеты."""
    segments = service.create_luck_route(
        request.query, lang, user_lat=request.user_lat, user_lng=request.user_lng
    )
    return TripRouteResponse(segments=segments)
