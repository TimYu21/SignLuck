import os

from app.api.routes import plates
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SignLuck API",
    description="API сервиса анализа вероятностей номерных знаков",
    version="1.0.0",
)

# Чтение списка разрешенных источников из переменных окружения
# Если переменная не задана, используется localhost для разработки
origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plates.router)


@app.get("/", tags=["Health"])
async def healthcheck():
    """Проверка доступности сервиса."""
    return {
        "status": "ok",
        "service": "signluck-backend",
    }
