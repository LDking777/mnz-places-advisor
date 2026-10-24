from typing import Any

from app.exceptions import InvalidUpstreamResponse
from app.schemas import PlaceDTO


def _as_coordinate(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _extract_category(categories: list) -> str:
    if not isinstance(categories, list):
        return ""
    for category in categories:
        if isinstance(category, str) and category.strip().startswith("tourism."):
            return category.strip()
    for category in categories:
        if isinstance(category, str) and category.strip():
            return category.strip()
    return ""


def feature_collection_to_places(payload: Any) -> list[PlaceDTO]:
    if not isinstance(payload, dict) or payload.get("type") != "FeatureCollection":
        raise InvalidUpstreamResponse("La respuesta no es un GeoJSON FeatureCollection.")

    features = payload.get("features")
    if not isinstance(features, list):
        raise InvalidUpstreamResponse("La respuesta no contiene una lista de features.")

    places: list[PlaceDTO] = []
    for feature in features:
        if not isinstance(feature, dict):
            continue

        properties = feature.get("properties")
        geometry = feature.get("geometry")
        if not isinstance(properties, dict) or not isinstance(geometry, dict):
            continue
        if geometry.get("type") != "Point":
            continue

        name = properties.get("name")
        categories = properties.get("categories")
        coordinates = geometry.get("coordinates")

        if not isinstance(name, str) or not name.strip():
            continue
        if not isinstance(categories, list) or not categories:
            continue
        if not isinstance(coordinates, list) or len(coordinates) < 2:
            continue

        category = _extract_category(categories)
        if not category:
            continue

        longitude = _as_coordinate(coordinates[0])
        latitude = _as_coordinate(coordinates[1])
        if latitude is None or longitude is None:
            continue
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            continue

        places.append(
            PlaceDTO(
                name=name.strip(),
                category=category,
                latitude=latitude,
                longitude=longitude,
            )
        )

    return places
