from typing import TypeVar, Generic, Type

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import Base

Model = TypeVar('Model', Base, Base)


class BaseGateway(Generic[Model]):
    def __init__(self, model: Type[Model], session: AsyncSession):
        self.model = model
        self.session = session

    def save(self, *models: Model):
        self.session.add_all(models)
