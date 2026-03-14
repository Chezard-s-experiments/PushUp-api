from dataclasses import dataclass
from uuid import UUID

from injection import injectable
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.users.aggregates import User
from src.core.users.ports.repo import UserRepository
from src.core.users.value_objects import Email
from src.infra.db.tables import UserTable


@injectable(on=UserRepository)
@dataclass(frozen=True)
class SQLAUserRepository(UserRepository):
    session: AsyncSession

    async def add(self, user: User) -> None:
        stmt = insert(UserTable).values(self._to_table_dict(user))
        await self.session.execute(stmt)

    async def update(self, user: User) -> None:
        await self.session.merge(self._to_table(user))

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserTable).where(UserTable.email == email)
        row = (await self.session.execute(stmt)).scalar_one_or_none()

        if row is None:
            return None

        return self._from_table(row)

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserTable).where(UserTable.id == user_id)
        row = (await self.session.execute(stmt)).scalar_one_or_none()

        if row is None:
            return None

        return self._from_table(row)

    def _to_table(self, user: User) -> UserTable:
        return UserTable(**self._to_table_dict(user))

    def _to_table_dict(self, user: User) -> dict[str, object]:
        return {
            "id": user.id,
            "email": str(user.email),
            "password_hash": user.hashed_password.get_secret_value(),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    def _from_table(self, table: UserTable) -> User:
        return User(
            id=table.id,
            email=Email(table.email),
            hashed_password=SecretStr(table.password_hash),
            first_name=table.first_name,
            last_name=table.last_name,
            created_at=table.created_at,
            updated_at=table.updated_at,
        )
