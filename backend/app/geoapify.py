from typing import Any

import httpx

from app.config import Settings
from app.exceptions import (
    InvalidUpstreamResponse,
    UpstreamServiceError,
    UpstreamTimeoutError,
)

PLACES_PATH = "/v2/places"


class GeoapifyClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.geoapify_base_url,
            timeout=httpx.Timeout(
                settings.request_timeout_seconds,
                connect=settings.connect_timeout_seconds,
            ),
            headers={
                "Accept": "application/json",
                "User-Agent": "manizales-tourist-recommendations/1.0",
            },
            transport=transport,
        )

    async def search_places(
        self,
        *,
        categories: str,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
    ) -> dict[str, Any]:
        params = {
            "categories": categories,
            "filter": f"circle:{longitude},{latitude},{radius_m}",
            "bias": f"proximity:{longitude},{latitude}",
            "limit": limit,
            "lang": self._settings.language,
            "apiKey": self._settings.geoapify_api_key,
        }

        try:
            response = await self._client.get(PLACES_PATH, params=params)
        except httpx.TimeoutException as exc:
            raise UpstreamTimeoutError(
                "Geoapify no respondió dentro del tiempo configurado."
            ) from exc
        except httpx.HTTPError as exc:
            raise UpstreamServiceError(
                "No fue posible comunicarse con Geoapify."
            ) from exc

        if response.status_code == 429:
            raise UpstreamServiceError(
                "Se alcanzó el límite de solicitudes de Geoapify. Intente más tarde."
            )
        if response.status_code >= 400:
            raise UpstreamServiceError(
                f"Geoapify respondió con estado HTTP {response.status_code}."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            raise InvalidUpstreamResponse(
                "Geoapify devolvió una respuesta que no es JSON válido."
            ) from exc

        if not isinstance(payload, dict):
            raise InvalidUpstreamResponse(
                "Geoapify devolvió un JSON con una estructura inesperada."
            )
        return payload

    async def aclose(self) -> None:
        await self._client.aclose()
