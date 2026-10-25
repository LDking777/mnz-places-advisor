from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.exceptions import ServiceError
from app.groq import GroqClient
from app.places_source import PostgresPlaceSource
from app.routers.chat import router as chat_router
from app.routers.places import router as places_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    pool = await asyncpg.create_pool(
        dsn=dsn,
        min_size=1,
        max_size=10,
        command_timeout=5.0,
    )
    app.state.db_pool = pool
    app.state.place_source = PostgresPlaceSource(pool)
    app.state.groq = GroqClient(settings)

    try:
        yield
    finally:
        await app.state.groq.aclose()
        await pool.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Gestor de Recomendaciones Turísticas - Manizales",
        description="API de recomendaciones turísticas respaldada por PostgreSQL/PostGIS y enriquecida con Groq.",
        version="1.3.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.frontend_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type"],
    )
    app.include_router(places_router)
    app.include_router(chat_router)

    @app.exception_handler(ServiceError)
    async def handle_service_error(_: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.get("/health", tags=["ops"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
