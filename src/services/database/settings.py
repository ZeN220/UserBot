from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import Settings
from .base import BaseGateway


class SettingsGateway(BaseGateway[Settings]):
    def __init__(self, session: AsyncSession):
        super().__init__(Settings, session)

    async def get_by_owner_id(self, owner_id: int, name: str) -> Optional[Settings]:
        query = select(Settings).where(
            Settings.owner_id == owner_id, Settings.name == name
        )
        result = await self.session.execute(query)
        return result.scalar()
