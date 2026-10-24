from fastapi import APIRouter, Depends, Query

from app.config import (
    DEFAULT_CATEGORY,
    MANIZALES_LAT,
    MANIZALES_LON,
    MANIZALES_RADIUS_M,
)
from app.dependencies import get_geoapify_client, get_groq_client
from app.geoapify import GeoapifyClient
from app.groq import GroqClient
from app.schemas import RecommendationResponse
from app.services import RecommendationService

router = APIRouter(prefix="/api/v1/places", tags=["places"])


@router.get(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Recomendaciones turísticas radiales en Manizales",
)
async def get_recommendations(
    category: str = Query(
        DEFAULT_CATEGORY,
        min_length=2,
        max_length=64,
        pattern=r"^[a-z0-9._]+$",
        description="Categoría de Geoapify (por defecto tourism.sights).",
    ),
    latitude: float = Query(MANIZALES_LAT, ge=-90, le=90),
    longitude: float = Query(MANIZALES_LON, ge=-180, le=180),
    radius_m: int = Query(MANIZALES_RADIUS_M, ge=100, le=50_000),
    limit: int = Query(20, ge=1, le=50),
    preferences: str | None = Query(
        default=None,
        max_length=200,
        description="Preferencias del usuario para que Groq ordene y justifique las recomendaciones.",
    ),
    client: GeoapifyClient = Depends(get_geoapify_client),
    groq_client: GroqClient = Depends(get_groq_client),
) -> RecommendationResponse:
    service = RecommendationService(client, groq_client)
    return await service.recommend(
        category=category,
        latitude=latitude,
        longitude=longitude,
        radius_m=radius_m,
        limit=limit,
        preferences=preferences,
    )
