from collections.abc import AsyncIterator

import pytest
from asgi_lifespan import LifespanManager
from faker import Faker
from httpx import ASGITransport, AsyncClient
from injection import get_instance, mod

from src.enums import SubProfile
from src.settings import Settings


@pytest.fixture(scope="function")
def faker() -> Faker:
    instance = get_instance(Faker)
    Faker.seed(0)
    return instance


@pytest.fixture(scope="session", autouse=True)
def settings() -> Settings:
    settings = Settings(_env_file=None)
    mod(SubProfile.GLOBAL).set_constant(settings, mode="override")
    return settings


@pytest.fixture(scope="function")
async def test_client() -> AsyncIterator[AsyncClient]:
    from main import app

    async with LifespanManager(app):
        async with AsyncClient(
            base_url="http://testserver",
            transport=ASGITransport(app=app),
        ) as client:
            yield client
