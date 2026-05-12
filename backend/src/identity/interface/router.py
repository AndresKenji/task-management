from __future__ import annotations

from fastapi import APIRouter, Depends

from shared.infrastructure import UnitOfWork, get_uow

from .dependencies import CognitoUser, current_user
from .schemas import ProfileOut


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ProfileOut)
async def get_my_profile(
    me: CognitoUser = Depends(current_user),
    uow: UnitOfWork = Depends(get_uow),
) -> ProfileOut:
    # TODO(milestone-4): implement.
    # Steps:
    #   1. async with uow:
    #   2.     repo = SqlAlchemyUserRepository(uow.session)
    #   3.     use_case = GetOrCreateProfile(repo)
    #   4.     user = await use_case.execute(
    #              GetOrCreateProfileCommand(
    #                  sub=me.sub, email=me.email, full_name=me.full_name,
    #              )
    #          )
    #   5. return user_to_profile(user)
    # Imports you'll need to add at the top of this file:
    #   from identity.application import GetOrCreateProfile, GetOrCreateProfileCommand
    #   from identity.infrastructure import SqlAlchemyUserRepository
    #   from .schemas import user_to_profile
    raise NotImplementedError


__all__ = ["router"]
