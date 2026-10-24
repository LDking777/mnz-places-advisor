import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_FILE)

MANIZALES_LAT = 5.068
MANIZALES_LON = -75.517
MANIZALES_RADIUS_M = 5000
DEFAULT_CATEGORY = "tourism.sights"


@dataclass(frozen=True)
class Settings:
    geoapify_api_key: str
    geoapify_base_url: str = "https://api.geoapify.com"
    request_timeout_seconds: float = 8.0
    connect_timeout_seconds: float = 3.0
    language: str = "es"
    frontend_origins: tuple[str, ...] = ("http://localhost:5173",)
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-20b"
    groq_timeout_seconds: float = 12.0


def _read_positive_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigurationError(f"La variable {name} debe ser un número.") from exc
    if value <= 0:
        raise ConfigurationError(f"La variable {name} debe ser mayor que cero.")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    api_key = os.getenv("GEOAPIFY_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "GEOAPIFY_API_KEY no está definida. Configúrela como variable de entorno "
            "o en backend/.env (nunca la escriba en el código fuente)."
        )

    origins_raw = os.getenv("FRONTEND_ORIGINS", "http://localhost:5173")
    origins = tuple(origin.strip() for origin in origins_raw.split(",") if origin.strip())
    if not origins:
        raise ConfigurationError("FRONTEND_ORIGINS debe contener al menos un origen.")

    return Settings(
        geoapify_api_key=api_key,
        geoapify_base_url=os.getenv("GEOAPIFY_BASE_URL", "https://api.geoapify.com").rstrip("/"),
        request_timeout_seconds=_read_positive_float("GEOAPIFY_TIMEOUT_SECONDS", 8.0),
        connect_timeout_seconds=_read_positive_float("GEOAPIFY_CONNECT_TIMEOUT_SECONDS", 3.0),
        language=os.getenv("GEOAPIFY_LANGUAGE", "es"),
        frontend_origins=origins,
        groq_api_key=os.getenv("GROQ_API_KEY", "").strip(),
        groq_base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/"),
        groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        groq_timeout_seconds=_read_positive_float("GROQ_TIMEOUT_SECONDS", 12.0),
    )
