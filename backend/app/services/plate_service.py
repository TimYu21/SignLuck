import logging
import math
import urllib.parse
from typing import List

from app.core.repository import CountryRepository
from app.schemas.plate import PlateCalculationResult
from app.schemas.trip import TripSegment
from app.services.calculator import PlateCalculator

logger = logging.getLogger(__name__)


class PlateService:
    """
    Сервис прикладного уровня для работы с номерными знаками.

    Инкапсулирует бизнес-логику:
    - перебор стран
    - фильтрацию невозможных вариантов
    - сортировку результатов
    """

    def __init__(
        self,
        repository: CountryRepository,
        calculator: PlateCalculator,
    ) -> None:
        self.repository = repository
        self.calculator = calculator

    def check_plate(self, query: str, lang: str = "ru") -> List[PlateCalculationResult]:
        """
        Проверяет комбинацию по всем поддерживаемым странам.

        Args:
            query (str): Поисковая комбинация пользователя.
            lang (str): Язык ответа ('ru' или 'en').

        Returns:
            List[PlateCalculationResult]: Отсортированный список результатов,
            где вероятность больше 0.
        """
        results: List[PlateCalculationResult] = []

        for country in self.repository.get_all():
            result = self.calculator.calculate_probability(query, country)
            if result is not None and result.probability > 0:
                # Локализация названия страны, если требуется
                if lang == "en" and country.country_name_en:
                    result.country_name = country.country_name_en
                results.append(result)

        # Сортировка по вероятности (убывание), затем по названию
        results.sort(key=lambda r: (-r.probability, r.country_name))

        logger.debug(
            "Calculated %d valid results for query '%s'",
            len(results),
            query,
        )

        return results

    def _calculate_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """Вычисляет расстояние между двумя точками."""
        R = 6371  # Радиус Земли в км
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def get_suggestions(self, query: str) -> List[str]:
        """Генерирует варианты замены букв на похожие цифры.

        Например: TOM -> T0M, BOSS -> B0SS, 80SS...
        """
        replacements = {
            "O": "0",
            "I": "1",
            "Z": "2",
            "E": "3",
            "S": "5",
            "B": "8",
        }

        results = set()

        # Рекурсивно генерируем все варианты замен
        def backtrack(index: int, current: str):
            if index == len(query):
                if current != query:
                    results.add(current)
                return

            char = query[index]
            # Вариант без замены
            backtrack(index + 1, current + char)

            # Вариант с заменой
            if char in replacements:
                backtrack(index + 1, current + replacements[char])

        backtrack(0, "")
        # Возвращаем топ-5 вариантов, отсортированных по алфавиту
        return sorted(list(results))[:5]

    def create_luck_route(
        self,
        query: str,
        lang: str = "ru",
        user_lat: float | None = None,
        user_lng: float | None = None,
    ) -> List[TripSegment]:
        """
        Строит маршрут по странам с высокой вероятностью встречи номера.

        Генерирует ссылки на внешний сервис покупки билетов (Google Flights).
        Если переданы координаты пользователя, маршрут оптимизируется по расстоянию.
        """
        # Получение базового расчета вероятностей
        results = self.check_plate(query, lang)

        # Выбор топ-5 стран-кандидатов
        candidates = results[:5]
        ordered_route = []

        # Оптимизация маршрута (Nearest Neighbor), если доступны координаты
        if user_lat is not None and user_lng is not None:
            current_lat, current_lng = user_lat, user_lng
            pool = candidates[:]

            while pool:
                # Ищем ближайшую страну из оставшихся
                pool.sort(
                    key=lambda x: self._calculate_distance(
                        current_lat, current_lng, x.lat, x.lng
                    )
                )
                nearest = pool.pop(0)
                ordered_route.append(nearest)
                current_lat, current_lng = nearest.lat, nearest.lng
        else:
            ordered_route = candidates

        segments = []
        prev_country_name = None

        for res in ordered_route:
            # Формируем ссылку на Google Flights
            encoded_country = urllib.parse.quote(res.country_name)

            if prev_country_name:
                # Перелет из предыдущей страны маршрута
                encoded_prev = urllib.parse.quote(prev_country_name)
                query_params = f"flights+from+{encoded_prev}+to+{encoded_country}"
            else:
                # Первый сегмент (от пользователя)
                query_params = (
                    f"flights+to+{encoded_country}"
                    if lang == "en"
                    else f"авиабилеты+в+{encoded_country}"
                )

            hl = "ru" if lang == "ru" else "en"
            booking_url = (
                f"https://www.google.com/travel/flights?q={query_params}&hl={hl}"
            )

            segments.append(
                TripSegment(
                    country_name=res.country_name,
                    country_code=res.country_code,
                    probability=res.probability,
                    booking_url=booking_url,
                    lat=res.lat,
                    lng=res.lng,
                )
            )
            prev_country_name = res.country_name

        return segments
