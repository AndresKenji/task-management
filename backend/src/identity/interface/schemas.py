from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from identity.domain import User


class ProfileOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    created_at: datetime


def user_to_profile(user: User) -> ProfileOut:
    return ProfileOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
    )
