from fastapi import APIRouter, Depends, Query

from app.config import (
    DEFAULT_CATEGORY,
    MANIZALES_LAT,
    MANIZALES_LON,
    MANIZALES_RADIUS_M,
)
from app.dependencies import get_groq_client, get_place_source
from app.groq import GroqClient
from app.places_source import PlaceSource
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
        description="Categoría de lugares (por defecto tourism.sights).",
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
    place_source: PlaceSource = Depends(get_place_source),
    groq_client: GroqClient = Depends(get_groq_client),
) -> RecommendationResponse:
    service = RecommendationService(place_source, groq_client)
    return await service.recommend(
        category=category,
        latitude=latitude,
        longitude=longitude,
        radius_m=radius_m,
        limit=limit,
        preferences=preferences,
    )
