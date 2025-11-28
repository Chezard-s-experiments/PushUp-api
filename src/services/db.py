from collections.abc import AsyncIterator

from injection import mod, scoped
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.enums import Scope, SubProfile
from src.settings import Settings


@mod(SubProfile.GLOBAL).injectable
def _db_engine_recipe(settings: Settings) -> AsyncEngine:
    return create_async_engine(settings.db.get_url())


@scoped(Scope.REQUEST)
async def _db_session_recipe(
    engine: AsyncEngine,
) -> AsyncIterator[AsyncSession]:  # pragma: no cover
    async with AsyncSession(engine) as session:
        async with session.begin():
            yield session
