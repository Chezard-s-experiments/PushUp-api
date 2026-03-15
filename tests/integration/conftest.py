"""Fixtures pour les tests d'intégration (DB réelle)."""

from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.infra.db.tables import Table
from src.settings import Settings


@pytest.fixture
async def db_engine(settings: Settings) -> AsyncIterator[AsyncEngine]:
    """Moteur async sur la base de test. Crée les tables au premier usage."""
    engine = create_async_engine(
        settings.db.get_url(),
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Table.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Session async avec transaction annulée en fin de test (isolation)."""
    async with db_engine.connect() as conn:
        await conn.begin()
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            yield session
        await conn.rollback()
