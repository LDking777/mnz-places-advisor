from typing import Any

from pydantic import BaseModel, Field


class PlaceDTO(BaseModel):
    name: str = Field(..., description="Nombre del lugar turístico")
    category: str = Field(..., description="Categoría principal del lugar")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    reason: str | None = Field(
        default=None,
        description="Justificación generada por IA para visitar este lugar",
    )


class RecommendationResponse(BaseModel):
    city: str = "Manizales"
    count: int = Field(..., ge=0)
    places: list[PlaceDTO]
    ai_enriched: bool = Field(default=False)
    ai_model: str | None = Field(default=None)
    fallback_reason: str | None = Field(default=None)


class SuggestedPlace(BaseModel):
    name: str
    category: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    reason: str | None = None


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=400)
    category: str = Field(default="tourism.sights", min_length=2, max_length=64, pattern=r"^[a-z0-9._]+$")
    latitude: float = Field(default=5.068, ge=-90, le=90)
    longitude: float = Field(default=-75.517, ge=-180, le=180)
    radius_m: int = Field(default=5000, ge=100, le=50000)
    limit: int = Field(default=12, ge=3, le=20)
    preferences: str | None = Field(default=None, max_length=200)


class ChatResponse(BaseModel):
    answer: str
    suggested_places: list[SuggestedPlace] = Field(default_factory=list)
    places_count: int = 0
    ai_enriched: bool = False
    ai_model: str | None = None
    fallback_reason: str | None = None
