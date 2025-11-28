from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvloop
from injection import adefine_scope
from injection.entrypoint import AsyncEntrypoint, Entrypoint, entrypointmaker
from injection.loaders import ProfileLoader, load_packages

from src.enums import Profile, Scope, SubProfile
from src.settings import Settings

_profile_loader = ProfileLoader(
    {
        Profile.DEFAULT: [SubProfile.GLOBAL],
        Profile.TEST: [SubProfile.GLOBAL],
    }
).init()


@asynccontextmanager
async def lifespan(
    profile: Profile,
    profile_loader: ProfileLoader = _profile_loader,
) -> AsyncIterator[None]:
    from src import core, services
    from src.infra import adapters, queries

    load_packages(adapters, core, queries, services)

    with profile_loader.load(profile):
        async with adefine_scope(Scope.LIFESPAN, kind="shared"):
            yield


@entrypointmaker(profile_loader=_profile_loader)
def main[**P, T](
    self: AsyncEntrypoint[P, T],
    settings: Settings,
) -> Entrypoint[P, T]:
    return (
        self.inject()
        .decorate(adefine_scope(Scope.REQUEST, kind="shared"))
        .decorate(lifespan(settings.profile, self.profile_loader))
        .async_to_sync(uvloop.run)
    )
