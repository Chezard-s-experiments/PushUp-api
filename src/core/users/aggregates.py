from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.core.users.value_objects import Email, HashedPassword


class User(BaseModel):
    id: UUID
    email: Email
    hashed_password: HashedPassword
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    updated_at: datetime

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "email": str(self.email),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
