from typing import Optional, List

from sqlalchemy.future import select
from sqlalchemy.sql import exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .base import BaseGateway
from src.database import Template, Attachment


class TemplateGateway(BaseGateway[Template]):
    def __init__(self, session: AsyncSession):
        super().__init__(Template, session)

    async def get(self, trigger: str, owner_id: int) -> Optional[Template]:
        query = select(Template).where(
            (Template.owner_id == owner_id) & (Template.trigger == trigger)
        ).options(joinedload(Template.attachments))
        async with self.session.begin():
            result = await self.session.execute(query)
        return result.scalar()

    async def exists(self, trigger: str, owner_id: int):
        query = select(exists(
            select(Template.id).where(
                (Template.owner_id == owner_id) & (Template.trigger == trigger)
            )
        ))
        async with self.session.begin():
            result = await self.session.execute(query)
        return result.scalar()

    async def create(
        self, trigger: str, owner_id: int,
        answer: str, attachments: Optional[List[str]] = None
    ) -> Template:
        async with self.session.begin():
            template = Template(trigger=trigger, answer=answer, owner_id=owner_id)
            if attachments is not None:
                attachments = [
                    Attachment(
                        template_id=template.id, document=attachment
                    ) for attachment in attachments
                ]
                template.attachments = attachments
            self.save(template)
            await self.session.commit()
        return template