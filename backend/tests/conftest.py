import os

import asyncpg
import pytest

os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ.setdefault("GROQ_API_KEY", "")


class _FakePool:
    async def close(self) -> None:
        pass


@pytest.fixture(autouse=True)
def _fake_asyncpg_pool(monkeypatch):
    async def fake_create_pool(*args, **kwargs):
        return _FakePool()

    monkeypatch.setattr(asyncpg, "create_pool", fake_create_pool)
