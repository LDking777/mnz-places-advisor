import pytest

from app.exceptions import InvalidUpstreamResponse
from app.transformers import feature_collection_to_places


def test_maps_geojson_to_simplified_places(geoapify_payload: dict) -> None:
    places = feature_collection_to_places(geoapify_payload)

    assert len(places) == 2
    assert [place.name for place in places] == [
        "Catedral Basílica de Manizales",
        "Mirador de Chipre",
    ]
    assert places[0].category == "tourism.sights"
    assert places[0].latitude == pytest.approx(5.0675)
    assert places[0].longitude == pytest.approx(-75.5167)
    assert places[1].category == "tourism.sights"


def test_dto_exposes_only_required_fields(geoapify_payload: dict) -> None:
    places = feature_collection_to_places(geoapify_payload)

    assert set(places[0].model_dump()) == {"name", "category", "latitude", "longitude"}


def test_skips_features_without_name_or_coordinates(geoapify_payload: dict) -> None:
    names = {place.name for place in feature_collection_to_places(geoapify_payload)}

    assert "Registro sin geometría" not in names
    assert all(isinstance(place.latitude, float) for place in feature_collection_to_places(geoapify_payload))


def test_rejects_payload_that_is_not_feature_collection() -> None:
    with pytest.raises(InvalidUpstreamResponse):
        feature_collection_to_places({"type": "Feature", "features": []})


def test_rejects_missing_features_list() -> None:
    with pytest.raises(InvalidUpstreamResponse):
        feature_collection_to_places({"type": "FeatureCollection"})
