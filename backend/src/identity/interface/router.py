from __future__ import annotations

from fastapi import APIRouter, Depends

from shared.infrastructure import UnitOfWork, get_uow

from .dependencies import CognitoUser, current_user
from .schemas import ProfileOut, user_to_profile
from identity.application import GetOrCreateProfile, GetOrCreateProfileCommand
from identity.infrastructure.sqlalchemy_repo import SqlAlchemyUserRepository


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ProfileOut)
async def get_my_profile(
    me: CognitoUser = Depends(current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> ProfileOut:
    async with uow:
        repo = SqlAlchemyUserRepository(uow.session)
        use_case = GetOrCreateProfile(repo)
        user = await use_case.execute(
            GetOrCreateProfileCommand(
                sub=me.sub,
                email=me.email,
                full_name=me.full_name,
            )
        )
        return user_to_profile(user)


__all__ = ["router"]
