import json
from typing import Any

from app.schemas import PlaceDTO


def apply_groq_enrichment(
    places: list[PlaceDTO],
    items: list[dict[str, Any]],
) -> tuple[list[PlaceDTO], bool]:
    if not places or not items:
        return places, False

    by_name: dict[str, PlaceDTO] = {}
    for place in places:
        by_name[place.name.lower()] = place

    ranked: list[tuple[int, PlaceDTO]] = []
    seen: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str):
            continue
        key = name.lower()
        place = by_name.get(key)
        if not place:
            continue
        rank = item.get("rank")
        try:
            rank_int = int(rank)
        except (TypeError, ValueError):
            rank_int = len(ranked) + 1

        reason = item.get("reason")
        if isinstance(reason, str) and reason.strip():
            place = place.model_copy(update={"reason": reason.strip()})
        ranked.append((rank_int, place))
        seen.add(key)

    for place in places:
        if place.name.lower() not in seen:
            ranked.append((10_000, place))

    ranked.sort(key=lambda pair: pair[0])
    return [place for _, place in ranked], True
