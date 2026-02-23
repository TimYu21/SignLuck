from unittest.mock import MagicMock

from app.api.routes.plates import get_plate_service
from app.main import app
from app.schemas.plate import PlateCalculationResult


def test_healthcheck(client):
    """Проверка доступности сервиса."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "signluck-backend"}


def test_check_endpoint_mocked(client):
    """Тест эндпоинта /check с моком сервиса."""

    # Создаем мок результата
    mock_result = PlateCalculationResult(
        country_name="TestLand",
        country_code="TL",
        lat=0,
        lng=0,
        probability=50.0,
        symbols=[],
        allowed_letters="ABC",
        pattern="AAA",
    )

    # Мокаем сервис
    mock_service = MagicMock()
    mock_service.check_plate.return_value = [mock_result]

    # Подменяем зависимость
    app.dependency_overrides[get_plate_service] = lambda: mock_service

    try:
        response = client.post("/check", json={"query": "ABC"})

        assert response.status_code == 200
        data = response.json()
        assert data["total_results"] == 1
        assert data["max_probability"] == 50.0
        assert data["results"][0]["country_name"] == "TestLand"

        # Проверяем, что сервис был вызван с правильными аргументами
        mock_service.check_plate.assert_called_with("ABC", "ru")

    finally:
        # Очищаем override после теста
        app.dependency_overrides = {}


def test_check_validation_error(client):
    """Тест валидации входных данных (слишком длинный запрос)."""
    response = client.post("/check", json={"query": "VERYLONGQUERYSTRING"})
    assert response.status_code == 422  # Unprocessable Entity

    response = client.post("/check", json={"query": ""})
    assert response.status_code == 422
