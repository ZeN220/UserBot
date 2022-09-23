from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import DeactivateModule
from .base import BaseGateway


class DeactivateModuleGateway(BaseGateway[DeactivateModule]):
    def __init__(self, session: AsyncSession):
        super().__init__(DeactivateModule, session)

    async def delete_by_owner_id_and_name(self, module: str, owner_id: int) -> None:
        query = delete(DeactivateModule).where(
            (DeactivateModule.module == module) & (DeactivateModule.session_owner_id == owner_id)
        )
        await self.session.execute(query)

    async def create(self, module: str, owner_id: int) -> DeactivateModule:
        async with self.session.begin():
            model = DeactivateModule(module=module, session_owner_id=owner_id)
            self.save(model)
        return model
