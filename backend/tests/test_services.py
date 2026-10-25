import pytest

from app.schemas import PlaceDTO
from app.services import ChatService, RecommendationService


class FakePlaceSource:
    def __init__(self, places: list[PlaceDTO]) -> None:
        self.places = places
        self.calls: list[dict] = []

    async def search_places(self, **kwargs) -> list[PlaceDTO]:
        self.calls.append(kwargs)
        return self.places


class FakeGroqClient:
    enabled = True
    model = "test-model"

    def __init__(self) -> None:
        self.rank_calls: list[tuple[list[dict], str | None]] = []
        self.answer_calls: list[tuple[str, list[dict]]] = []

    async def rank_places(self, places, *, preferences=None):
        self.rank_calls.append((places, preferences))
        return [
            {"name": "Mirador de Chipre", "rank": 1, "reason": "Mejor vista de la ciudad."},
            {"name": "Catedral Basílica de Manizales", "rank": 2, "reason": "Patrimonio histórico."},
        ]

    async def answer_with_places(self, question, places):
        self.answer_calls.append((question, places))
        return {
            "answer": "Visita el mirador al atardecer.",
            "suggested_places": [
                {"name": "Mirador de Chipre", "reason": "Ideal para el atardecer."},
                {"name": "Lugar inventado", "reason": "No existe en la fuente."},
            ],
        }


def _places() -> list[PlaceDTO]:
    return [
        PlaceDTO(
            name="Catedral Basílica de Manizales",
            category="tourism.sights",
            latitude=5.0675,
            longitude=-75.5167,
        ),
        PlaceDTO(
            name="Mirador de Chipre",
            category="tourism.sights",
            latitude=5.0689,
            longitude=-75.528,
        ),
    ]


@pytest.mark.asyncio
async def test_recommendation_service_keeps_groq_ranking_and_reasons() -> None:
    source = FakePlaceSource(_places())
    groq = FakeGroqClient()
    service = RecommendationService(source, groq)

    result = await service.recommend(
        category="tourism.sights",
        latitude=5.068,
        longitude=-75.517,
        radius_m=5000,
        limit=10,
        preferences="atardeceres",
    )

    assert result["ai_enriched"] is True
    assert result["ai_model"] == "test-model"
    assert [place.name for place in result["places"]] == [
        "Mirador de Chipre",
        "Catedral Basílica de Manizales",
    ]
    assert result["places"][0].reason == "Mejor vista de la ciudad."
    assert source.calls == [
        {
            "categories": "tourism.sights",
            "latitude": 5.068,
            "longitude": -75.517,
            "radius_m": 5000,
            "limit": 10,
        }
    ]
    assert groq.rank_calls == [
        (
            [
                {"name": "Catedral Basílica de Manizales", "category": "tourism.sights"},
                {"name": "Mirador de Chipre", "category": "tourism.sights"},
            ],
            "atardeceres",
        )
    ]


@pytest.mark.asyncio
async def test_chat_service_discards_places_not_returned_by_source() -> None:
    source = FakePlaceSource(_places())
    groq = FakeGroqClient()
    service = ChatService(source, groq)

    result = await service.ask(
        question="¿Qué mirador me recomiendas?",
        category="tourism.sights",
        latitude=5.068,
        longitude=-75.517,
        radius_m=5000,
        limit=10,
    )

    assert result["ai_enriched"] is True
    assert result["places_count"] == 2
    assert result["suggested_places"] == [
        {
            "name": "Mirador de Chipre",
            "category": "tourism.sights",
            "latitude": 5.0689,
            "longitude": -75.528,
            "reason": "Ideal para el atardecer.",
        }
    ]
    assert groq.answer_calls[0][0] == "¿Qué mirador me recomiendas?"
    assert len(groq.answer_calls[0][1]) == 2
