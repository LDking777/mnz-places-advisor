import json
from typing import Any

import httpx

from app.config import Settings
from app.exceptions import UpstreamServiceError, UpstreamTimeoutError


class GroqEnrichmentError(Exception):
    pass


class GroqClient:
    def __init__(self, settings: Settings, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.groq_base_url,
            timeout=httpx.Timeout(settings.groq_timeout_seconds, connect=3.0),
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "manizales-tourist-recommendations/1.0",
            },
            transport=transport,
        )

    @property
    def enabled(self) -> bool:
        return bool(self._settings.groq_api_key)

    @property
    def model(self) -> str:
        return self._settings.groq_model

    async def rank_places(
        self,
        places: list[dict[str, Any]],
        *,
        preferences: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.enabled:
            raise GroqEnrichmentError("GROQ_API_KEY no configurada")
        if not places:
            return []

        preference_text = preferences.strip() if preferences and preferences.strip() else "Sin preferencias especificadas. Priorice lugares representativos de Manizales para turismo."

        system_prompt = (
            "Eres un recomendador turístico experto en Manizales, Caldas (Colombia). "
            "Debes ordenar los lugares que te envían y dar un motivo corto y honesto. "
            "Responde ÚNICAMENTE con un objeto JSON válido que tenga la clave 'items'. "
            "Cada item debe tener: name, rank (entero 1-n), reason (máximo 80 palabras, conciso). "
            "No inventes lugares nuevos. Usa exactamente los nombres enviados."
        )

        user_prompt = json.dumps(
            {
                "city": "Manizales",
                "preferences": preference_text,
                "places": places,
            },
            ensure_ascii=False,
        )

        payload = {
            "model": self._settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 800,
            "response_format": {"type": "json_object"},
        }

        try:
            response = await self._client.post("/chat/completions", json=payload)
        except httpx.TimeoutException as exc:
            raise UpstreamTimeoutError("Groq no respondió a tiempo.") from exc
        except httpx.HTTPError as exc:
            raise UpstreamServiceError("No fue posible comunicarse con Groq.") from exc

        if response.status_code == 429:
            raise UpstreamServiceError("Límite de solicitudes alcanzado en Groq.")
        if response.status_code >= 400:
            raise UpstreamServiceError(f"Groq respondió con estado HTTP {response.status_code}.")

        try:
            data = response.json()
        except ValueError as exc:
            raise GroqEnrichmentError("Groq devolvió una respuesta que no es JSON válido.") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GroqEnrichmentError("Estructura inesperada en respuesta de Groq.") from exc

        try:
            parsed = json.loads(content)
        except ValueError as exc:
            raise GroqEnrichmentError("El contenido de Groq no es JSON válido.") from exc

        items = parsed.get("items")
        if not isinstance(items, list):
            raise GroqEnrichmentError("Groq no devolvió 'items' como lista.")
        return items

    async def answer_with_places(
        self,
        question: str,
        places: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.enabled:
            raise GroqEnrichmentError("GROQ_API_KEY no configurada")
        if not places:
            raise GroqEnrichmentError("No hay lugares disponibles para el asistente.")

        system_prompt = (
            "Eres 'Manizales Tour Guide', un guía turístico local de Manizales, Caldas (Colombia). "
            "Tu ÚNICA fuente de verdad es la lista JSON de lugares que recibes. "
            "NO inventes, NO añadas lugares, NO inventes precios, direcciones, horarios o datos que no estén ahí. "
            "Si la pregunta no se puede responder con esos lugares, dilo honestamente. "
            "Responde en español, práctico, ameno y conciso. "
            "Siempre prioriza recomendaciones usando SOLO nombres de la lista. "
            "Responde ÚNICAMENTE con un objeto JSON válido con estas claves: "
            "'answer' (string, respuesta completa para el usuario), "
            "'suggested_places' (array con objetos {name, reason}). Usa únicamente nombres que existan en la lista."
        )

        user_prompt = json.dumps(
            {
                "city": "Manizales",
                "question": question,
                "places": places,
            },
            ensure_ascii=False,
        )

        payload = {
            "model": self._settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.25,
            "max_tokens": 900,
            "response_format": {"type": "json_object"},
        }

        try:
            response = await self._client.post("/chat/completions", json=payload)
        except httpx.TimeoutException as exc:
            raise UpstreamTimeoutError("Groq no respondió a tiempo.") from exc
        except httpx.HTTPError as exc:
            raise UpstreamServiceError("No fue posible comunicarse con Groq.") from exc

        if response.status_code == 429:
            raise UpstreamServiceError("Límite de solicitudes alcanzado en Groq.")
        if response.status_code >= 400:
            raise UpstreamServiceError(f"Groq respondió con estado HTTP {response.status_code}.")

        try:
            data = response.json()
        except ValueError as exc:
            raise GroqEnrichmentError("Groq devolvió una respuesta que no es JSON válido.") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GroqEnrichmentError("Estructura inesperada en respuesta de Groq.") from exc

        try:
            parsed = json.loads(content)
        except ValueError as exc:
            raise GroqEnrichmentError("El contenido de Groq no es JSON válido.") from exc

        if not isinstance(parsed.get("answer"), str):
            raise GroqEnrichmentError("Groq no devolvió 'answer' como string.")
        if not isinstance(parsed.get("suggested_places"), list):
            parsed["suggested_places"] = []
        return parsed

    async def aclose(self) -> None:
        await self._client.aclose()
