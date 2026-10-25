from app.enrichment import apply_groq_enrichment
from app.exceptions import ServiceError
from app.groq import GroqClient
from app.places_source import PlaceSource


class RecommendationService:
    def __init__(self, place_source: PlaceSource, groq_client: GroqClient | None = None) -> None:
        self._place_source = place_source
        self._groq = groq_client

    async def recommend(
        self,
        *,
        category: str,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        preferences: str | None = None,
    ):
        places = await self._place_source.search_places(
            categories=category,
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            limit=limit,
        )

        if not self._groq or not self._groq.enabled or not places:
            return {
                "count": len(places),
                "places": places,
                "ai_enriched": False,
                "ai_model": None,
                "fallback_reason": None if self._groq and self._groq.enabled else "Groq no configurado.",
            }

        try:
            slim = [{"name": place.name, "category": place.category} for place in places]
            items = await self._groq.rank_places(slim, preferences=preferences)
            enriched, ok = apply_groq_enrichment(places, items)
            if ok and enriched:
                return {
                    "count": len(enriched),
                    "places": enriched,
                    "ai_enriched": True,
                    "ai_model": self._groq.model,
                    "fallback_reason": None,
                }
            raise ServiceError("No fue posible aplicar el ranking de Groq.")
        except ServiceError:
            return {
                "count": len(places),
                "places": places,
                "ai_enriched": False,
                "ai_model": None,
                "fallback_reason": "Groq no disponible, se muestra el orden original de la fuente de lugares.",
            }
        except Exception:
            return {
                "count": len(places),
                "places": places,
                "ai_enriched": False,
                "ai_model": None,
                "fallback_reason": "Groq no disponible, se muestra el orden original de la fuente de lugares.",
            }


class ChatService:
    def __init__(self, place_source: PlaceSource, groq_client: GroqClient | None = None) -> None:
        self._place_source = place_source
        self._groq = groq_client

    async def ask(
        self,
        question: str,
        category: str,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
    ):
        places = await self._place_source.search_places(
            categories=category,
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
            limit=limit,
        )
        slim = [
            {"name": p.name, "category": p.category, "latitude": p.latitude, "longitude": p.longitude}
            for p in places
        ]

        if not self._groq or not self._groq.enabled or not slim:
            return {
                "answer": "El asistente con IA no está disponible. Aquí tienes los lugares encontrados cerca de Manizales:",
                "suggested_places": [
                    {"name": p.name, "category": p.category, "latitude": p.latitude, "longitude": p.longitude}
                    for p in places
                ],
                "places_count": len(places),
                "ai_enriched": False,
                "ai_model": None,
                "fallback_reason": "Groq no configurado o sin resultados.",
            }

        try:
            result = await self._groq.answer_with_places(question, slim)
            answer = result.get("answer") or "Te dejo algunas recomendaciones basadas en los lugares disponibles."
            suggested = result.get("suggested_places") or []

            enriched_suggested = []
            by_name = {p.name.lower(): p for p in places}
            for item in suggested:
                if not isinstance(item, dict):
                    continue
                name = item.get("name")
                if not isinstance(name, str):
                    continue
                place = by_name.get(name.lower())
                if not place:
                    continue
                enriched_suggested.append(
                    {
                        "name": place.name,
                        "category": place.category,
                        "latitude": place.latitude,
                        "longitude": place.longitude,
                        "reason": item.get("reason") if isinstance(item.get("reason"), str) else None,
                    }
                )

            if not enriched_suggested:
                enriched_suggested = [
                    {"name": p.name, "category": p.category, "latitude": p.latitude, "longitude": p.longitude}
                    for p in places[:5]
                ]

            return {
                "answer": answer,
                "suggested_places": enriched_suggested,
                "places_count": len(places),
                "ai_enriched": True,
                "ai_model": self._groq.model,
                "fallback_reason": None,
            }
        except Exception:
            return {
                "answer": "No pude generar una respuesta con IA ahora. Aquí tienes los lugares que encontré cerca de Manizales:",
                "suggested_places": [
                    {"name": p.name, "category": p.category, "latitude": p.latitude, "longitude": p.longitude}
                    for p in places[:6]
                ],
                "places_count": len(places),
                "ai_enriched": False,
                "ai_model": None,
                "fallback_reason": "Error al conectar con Groq, se muestran sugerencias basadas en la fuente de lugares.",
            }
