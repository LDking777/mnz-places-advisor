from typing import Any, Protocol

from app.exceptions import DatabaseUnavailableError
from app.schemas import PlaceDTO

PLACES_QUERY = """
SELECT
    TRIM(name) AS name,
    TRIM(category) AS category,
    ST_Y(geom::geometry) AS latitude,
    ST_X(geom::geometry) AS longitude
FROM places
WHERE (
    category = $1
    OR category LIKE $1 || '.%'
    OR $1 LIKE category || '.%'
    OR EXISTS (
        SELECT 1
        FROM unnest(categories) AS stored_category
        WHERE stored_category = $1
           OR stored_category LIKE $1 || '.%'
           OR $1 LIKE stored_category || '.%'
    )
)
AND ST_DWithin(
    geom,
    ST_SetSRID(ST_MakePoint($2, $3), 4326)::geography,
    $4
)
ORDER BY geom <-> ST_SetSRID(ST_MakePoint($2, $3), 4326)::geography
LIMIT $5
"""


class PlaceSource(Protocol):
    async def search_places(
        self,
        *,
        categories: str,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
    ) -> list[PlaceDTO]: ...


class PostgresPlaceSource:
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    async def search_places(
        self,
        *,
        categories: str,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
    ) -> list[PlaceDTO]:
        try:
            records = await self._pool.fetch(
                PLACES_QUERY,
                categories,
                longitude,
                latitude,
                radius_m,
                limit,
            )
        except Exception as exc:
            raise DatabaseUnavailableError from exc

        return [
            PlaceDTO(
                name=str(record["name"]).strip(),
                category=str(record["category"]).strip(),
                latitude=float(record["latitude"]),
                longitude=float(record["longitude"]),
            )
            for record in records
        ]
