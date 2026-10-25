import pytest

from app.exceptions import DatabaseUnavailableError
from app.places_source import PostgresPlaceSource


class FakePool:
    def __init__(self, rows: list[dict] | None = None, error: Exception | None = None) -> None:
        self.rows = rows or []
        self.error = error
        self.query = ""
        self.args: tuple = ()

    async def fetch(self, query: str, *args):
        self.query = query
        self.args = args
        if self.error:
            raise self.error
        return self.rows


@pytest.mark.asyncio
async def test_postgres_place_source_maps_rows_and_uses_postgis_query() -> None:
    pool = FakePool(
        rows=[
            {
                "name": " Catedral Basílica de Manizales ",
                "category": "tourism.sights",
                "latitude": 5.0675,
                "longitude": -75.5169,
            },
            {
                "name": "Mirador de Chipre",
                "category": "tourism.sights",
                "latitude": 5.0689,
                "longitude": -75.528,
            },
        ]
    )
    source = PostgresPlaceSource(pool)

    places = await source.search_places(
        categories="tourism.sights",
        latitude=5.068,
        longitude=-75.517,
        radius_m=5000,
        limit=10,
    )

    assert [place.name for place in places] == [
        "Catedral Basílica de Manizales",
        "Mirador de Chipre",
    ]
    assert places[0].latitude == pytest.approx(5.0675)
    assert places[0].longitude == pytest.approx(-75.5169)
    assert "ST_DWithin" in pool.query
    assert "<->" in pool.query
    assert "LIMIT $5" in pool.query
    assert pool.args == ("tourism.sights", -75.517, 5.068, 5000, 10)


@pytest.mark.asyncio
async def test_postgres_place_source_translates_database_errors() -> None:
    source = PostgresPlaceSource(FakePool(error=RuntimeError("connection refused")))

    with pytest.raises(DatabaseUnavailableError):
        await source.search_places(
            categories="tourism.sights",
            latitude=5.068,
            longitude=-75.517,
            radius_m=5000,
            limit=10,
        )
