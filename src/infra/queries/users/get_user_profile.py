from typing import NamedTuple

from cq import query_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.users.queries.get_user_profile import (
    GetUserProfileQuery,
    UserProfileView,
)
from src.infra.db.tables import UserTable


@query_handler
class GetUserProfileHandler(NamedTuple):
    session: AsyncSession

    async def handle(
        self,
        query: GetUserProfileQuery,
    ) -> UserProfileView | None:
        stmt = select(
            UserTable.id,
            UserTable.email,
            UserTable.first_name,
            UserTable.last_name,
            UserTable.created_at,
            UserTable.updated_at,
        ).where(UserTable.id == query.user_id)

        row = (await self.session.execute(stmt)).mappings().one_or_none()

        if row is None:
            return None

        return UserProfileView.model_validate(row)
