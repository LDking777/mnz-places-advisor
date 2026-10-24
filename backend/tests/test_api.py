from fastapi.testclient import TestClient

from app.dependencies import get_geoapify_client
from app.exceptions import UpstreamTimeoutError
from app.main import app


class FakeGeoapifyClient:
    def __init__(self, payload: dict | None = None, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error
        self.calls: list[dict] = []

    async def search_places(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.payload


def test_endpoint_returns_simplified_places(geoapify_payload: dict) -> None:
    fake = FakeGeoapifyClient(payload=geoapify_payload)
    app.dependency_overrides[get_geoapify_client] = lambda: fake

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
    }
    assert "features" not in body
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
    fake = FakeGeoapifyClient(error=UpstreamTimeoutError())
    app.dependency_overrides[get_geoapify_client] = lambda: fake

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/places/recommendations")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 504
    assert response.json()["error"]["code"] == "upstream_timeout"


def test_endpoint_validates_query_parameters() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/places/recommendations?limit=0")

    assert response.status_code == 422
