from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from identity.application import UserRepository
from identity.domain import User

from .models import UserModel, domain_to_model, model_to_domain


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        await self._session.merge(domain_to_model(user))

    async def get(self, user_id: UUID) -> User:
        model = await self._session.get(UserModel, user_id)
        if model is None:
            raise KeyError(f"user {user_id} not found")
        return model_to_domain(model)
