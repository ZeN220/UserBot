from typing import TYPE_CHECKING

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.dispatching import UserEvent


class FilterResult(BaseModel):
    result: bool = Field(None, description='Result of checking filter')
    context: dict = Field(None, description='Values from filter')


class BaseFilter(ABC):
    @abstractmethod
    async def check(self, event: UserEvent) -> FilterResult:
        ...
