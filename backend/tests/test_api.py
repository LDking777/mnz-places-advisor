from fastapi.testclient import TestClient

from app.dependencies import get_groq_client, get_place_source
from app.exceptions import DatabaseUnavailableError, UpstreamTimeoutError
from app.main import app
from app.schemas import PlaceDTO


class FakePlaceSource:
    def __init__(self, places: list[PlaceDTO] | None = None, error: Exception | None = None) -> None:
        self.places = places or []
        self.error = error
        self.calls: list[dict] = []

    async def search_places(self, **kwargs) -> list[PlaceDTO]:
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.places


class DisabledGroqClient:
    enabled = False
    model = None


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


def test_endpoint_returns_simplified_places() -> None:
    fake = FakePlaceSource(places=_places())
    app.dependency_overrides[get_place_source] = lambda: fake
    app.dependency_overrides[get_groq_client] = lambda: DisabledGroqClient()

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/places/recommendations")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["city"] == "Manizales"
    assert body["count"] == 2
    assert body["places"][0] == {
        "name": "Catedral Basílica de Manizales",
        "category": "tourism.sights",
        "latitude": 5.0675,
        "longitude": -75.5167,
        "reason": None,
    }
    assert fake.calls == [
        {
            "categories": "tourism.sights",
            "latitude": 5.068,
            "longitude": -75.517,
            "radius_m": 5000,
            "limit": 20,
        }
    ]


def test_endpoint_returns_504_when_upstream_times_out() -> None:
    fake = FakePlaceSource(error=UpstreamTimeoutError())
    app.dependency_overrides[get_place_source] = lambda: fake
    app.dependency_overrides[get_groq_client] = lambda: DisabledGroqClient()

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/places/recommendations")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 504
    assert response.json()["error"]["code"] == "upstream_timeout"


def test_endpoint_returns_503_when_database_is_unavailable() -> None:
    fake = FakePlaceSource(error=DatabaseUnavailableError())
    app.dependency_overrides[get_place_source] = lambda: fake
    app.dependency_overrides[get_groq_client] = lambda: DisabledGroqClient()

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/places/recommendations")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "database_unavailable"


def test_endpoint_validates_query_parameters() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/places/recommendations?limit=0")

    assert response.status_code == 422
