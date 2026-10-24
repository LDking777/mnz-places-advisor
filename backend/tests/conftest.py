import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("GEOAPIFY_API_KEY", "clave-solo-para-pruebas")

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def geoapify_payload() -> dict:
    return json.loads((FIXTURES_DIR / "geoapify_places.json").read_text(encoding="utf-8"))
