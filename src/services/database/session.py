from typing import List

from sqlalchemy import select, delete
from sqlalchemy.orm import subqueryload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import SessionModel
from .base import BaseGateway


class SessionGateway(BaseGateway[SessionModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(SessionModel, session)

    async def get_all_with_deactivate_modules(self) -> List[SessionModel]:
        query = select(SessionModel).options(
            subqueryload(SessionModel.deactivate_modules)
        )
        async with self.session.begin():
            result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_group_id(self, group_id: int) -> List[SessionModel]:
        query = select(SessionModel).where(SessionModel.group_id == group_id)
        async with self.session.begin():
            result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all(self) -> List[SessionModel]:
        query = select(SessionModel)
        async with self.session.begin():
            result = await self.session.execute(query)
        return result.scalars().all()

    async def create(
        self, owner_id: int, user_token: str, group_id: int,
        group_token: str, commands_prefix: str, delete_command_after: bool = True
    ) -> SessionModel:
        async with self.session.begin():
            session = SessionModel(
                owner_id=owner_id, user_token=user_token, group_token=group_token,
                commands_prefix=commands_prefix, delete_command_after=delete_command_after,
                group_id=group_id
            )
            self.save(session)
            await self.session.commit()
        return session

    async def delete_by_owner_id(self, owner_id: int) -> None:
        query = delete(SessionModel).where(
            SessionModel.owner_id == owner_id
        )
        async with self.session.begin():
            await self.session.execute(query)

    async def delete_by_user_token(self, user_token: str) -> None:
        query = delete(SessionModel).where(
            SessionModel.user_token == user_token
        )
        async with self.session.begin():
            await self.session.execute(query)
