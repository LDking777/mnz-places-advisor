from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config import Settings
from app.exceptions import UpstreamServiceError, UpstreamTimeoutError
from app.geoapify import GeoapifyClient


def _settings() -> Settings:
    return Settings(
        geoapify_api_key="clave-de-prueba",
        request_timeout_seconds=2.0,
        connect_timeout_seconds=1.0,
    )


def _mock_response(payload: dict, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    return response


@pytest.mark.asyncio
async def test_uses_manizales_radial_filter_and_env_api_key(geoapify_payload: dict) -> None:
    mocked_get = AsyncMock(return_value=_mock_response(geoapify_payload))

    with patch("httpx.AsyncClient.get", new=mocked_get):
        client = GeoapifyClient(_settings())
        payload = await client.search_places(
            categories="tourism.sights",
            latitude=5.068,
            longitude=-75.517,
            radius_m=5000,
            limit=10,
        )
        await client.aclose()

    assert payload == geoapify_payload
    mocked_get.assert_awaited_once()
    args, kwargs = mocked_get.await_args
    assert args[0] == "/v2/places"
    assert kwargs["params"] == {
        "categories": "tourism.sights",
        "filter": "circle:-75.517,5.068,5000",
        "bias": "proximity:-75.517,5.068",
        "limit": 10,
        "lang": "es",
        "apiKey": "clave-de-prueba",
    }


@pytest.mark.asyncio
async def test_translates_timeout_to_service_error() -> None:
    mocked_get = AsyncMock(side_effect=httpx.ReadTimeout("timeout simulado"))

    with patch("httpx.AsyncClient.get", new=mocked_get):
        client = GeoapifyClient(_settings())
        with pytest.raises(UpstreamTimeoutError):
            await client.search_places(
                categories="tourism.sights",
                latitude=5.068,
                longitude=-75.517,
                radius_m=5000,
                limit=10,
            )
        await client.aclose()


@pytest.mark.asyncio
async def test_translates_http_error_status() -> None:
    mocked_get = AsyncMock(return_value=_mock_response({}, status_code=500))

    with patch("httpx.AsyncClient.get", new=mocked_get):
        client = GeoapifyClient(_settings())
        with pytest.raises(UpstreamServiceError):
            await client.search_places(
                categories="tourism.sights",
                latitude=5.068,
                longitude=-75.517,
                radius_m=5000,
                limit=10,
            )
        await client.aclose()
