from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GetUserProfileQuery(BaseModel):
    user_id: UUID


class UserProfileView(BaseModel):
    id: UUID
    email: str
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    updated_at: datetime
