import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.exceptions import ServiceError
from app.geoapify import GeoapifyClient
from app.groq import GroqClient
from app.routers.chat import router as chat_router
from app.routers.places import router as places_router

logger = logging.getLogger("manizales.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.geoapify = GeoapifyClient(settings)
    app.state.groq = GroqClient(settings)
    try:
        yield
    finally:
        await app.state.geoapify.aclose()
        await app.state.groq.aclose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Gestor de Recomendaciones Turísticas - Manizales",
        description="API intermediaria que transforma Geoapify Places y puede enriquecer con Groq.",
        version="1.2.0",
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
