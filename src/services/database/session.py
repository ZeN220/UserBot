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

    async def delete_by_user_token(self, user_token: str) -> None:
        query = delete(SessionModel).where(
            SessionModel.user_token == user_token
        )
        async with self.session.begin():
            await self.session.execute(query)
