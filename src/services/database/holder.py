from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .session import SessionGateway
from .template import TemplateGateway


@dataclass
class HolderGateway:
    database_session: AsyncSession
    template: TemplateGateway = field(init=False)
    session: SessionGateway = field(init=False)

    def __post_init__(self):
        self.template = TemplateGateway(self.database_session)
        self.session = SessionGateway(self.database_session)

    async def run_raw_query(self, query: str):
        query = text(query)
        async with self.database_session.begin():
            result = await self.database_session.execute(query)
        return result.all()
