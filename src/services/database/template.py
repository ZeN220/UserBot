from typing import Optional, List

from sqlalchemy import select, delete
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

    async def get_triggers_by_owner_id(self, owner_id: int) -> Optional[List[Template]]:
        query = select(Template.trigger).where(Template.owner_id == owner_id)
        async with self.session.begin():
            result = await self.session.execute(query)
        return result.scalars().all()

    async def exists(self, trigger: str, owner_id: int) -> bool:
        query = select(exists(
            select(Template.id).where(
                (Template.owner_id == owner_id) & (Template.trigger == trigger)
            )
        ))
        async with self.session.begin():
            result = await self.session.execute(query)
        return result.scalar()

    async def delete(self, trigger: str, owner_id: int) -> None:
        query = delete(Template).where((Template.trigger == trigger) & (owner_id == owner_id))
        async with self.session.begin():
            await self.session.execute(query)

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
