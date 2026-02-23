from unittest.mock import MagicMock

from app.schemas.country import CountrySchema
from app.services.plate_service import PlateService


def test_check_plate_sorting(calculator):
    """Проверка, что результаты сортируются по вероятности (от большей к меньшей)."""
    repo_mock = MagicMock()

    # Страна А: вероятность будет низкой (мало вариантов)
    c1 = CountrySchema(
        country_code="AA",
        country_name="LowProb",
        pattern="0",
        lat=0,
        lng=0,
        allowed_letters="",
    )
    # Страна Б: вероятность будет высокой (мало символов в шаблоне -> выше шанс совпадения одной цифры)
    # Для теста проще замокать calculate_probability, но мы используем реальный калькулятор
    # Pattern "0" (10 вариантов). Query "7". Prob = 10%.
    c2 = CountrySchema(
        country_code="BB",
        country_name="HighProb",
        pattern="00000",
        lat=0,
        lng=0,
        allowed_letters="",
    )

    repo_mock.get_all.return_value = [c1, c2]

    service = PlateService(repo_mock, calculator)
    results = service.check_plate("7")

    assert len(results) == 2
    assert results[0].country_name == "HighProb"
    assert results[1].country_name == "LowProb"
    assert results[0].probability > results[1].probability


def test_suggestions_generation(calculator):
    """Тест генерации подсказок (Leet speak)."""
    repo_mock = MagicMock()
    service = PlateService(repo_mock, calculator)

    # BOSS -> B0SS, 80SS, etc.
    suggestions = service.get_suggestions("BOSS")

    assert "80SS" in suggestions
    assert len(suggestions) > 0


def test_route_nearest_neighbor(calculator):
    """Тест построения маршрута методом ближайшего соседа."""
    repo_mock = MagicMock()

    # Создаем 3 страны с одинаковым шаблоном (чтобы вероятность была > 0)
    # Расположим их на одной линии: User(0,0) -> Near(1,1) -> Mid(5,5) -> Far(10,10)
    c_far = CountrySchema(
        country_code="FF", country_name="Far", pattern="0", lat=10, lng=10
    )
    c_near = CountrySchema(
        country_code="NN", country_name="Near", pattern="0", lat=1, lng=1
    )
    c_mid = CountrySchema(
        country_code="MM", country_name="Mid", pattern="0", lat=5, lng=5
    )

    repo_mock.get_all.return_value = [c_far, c_near, c_mid]

    service = PlateService(repo_mock, calculator)

    # Запрос "7" даст совпадение во всех странах
    segments = service.create_luck_route("7", user_lat=0, user_lng=0)

    assert len(segments) == 3
    # Первый сегмент должен быть Near
    assert segments[0].country_name == "Near"
    # Второй Mid
    assert segments[1].country_name == "Mid"
    # Третий Far
    assert segments[2].country_name == "Far"

    # Проверка генерации ссылок
    assert "google.com/travel/flights" in segments[0].booking_url
