from app.api.routes import plates
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SignLuck API",
    description="API сервиса анализа вероятностей номерных знаков",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
