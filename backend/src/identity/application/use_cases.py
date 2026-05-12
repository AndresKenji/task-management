from __future__ import annotations

from identity.domain import User

from .commands import GetOrCreateProfileCommand
from .ports import UserRepository


class GetOrCreateProfile:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def execute(self, cmd: GetOrCreateProfileCommand) -> User:
        # TODO(milestone-4): implement the find-or-create pattern.
        # Steps:
        #   1. try: existing = await self._repo.get(cmd.sub); return existing
        #   2. except KeyError:
        #        user = User.create(sub=cmd.sub, email=cmd.email, full_name=cmd.full_name)
        #        await self._repo.add(user)
        #        return user
        # No update path for now; we just return whatever is in the repo on hit.
        raise NotImplementedError
