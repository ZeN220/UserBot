from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.dispatching import UserEvent

if TYPE_CHECKING:
    from src.commands.base.command import Command


class FilterResult(BaseModel):
    result: bool = Field(None, description='Result of checking filter')
    context: dict = Field(None, description='Values from filter')


class BaseFilter(ABC):
    @abstractmethod
    async def check(self, event: UserEvent, command: 'Command') -> FilterResult:
        ...

    def __or__(self, other: 'BaseFilter'):
        return OrFilter(self, other)


class OrFilter(BaseFilter):
    def __init__(self, *filters: BaseFilter):
        self.filters = filters

    async def check(self, event: UserEvent, command: 'Command') -> FilterResult:
        for filter_ in self.filters:
            response = await filter_.check(event, command)
            if response.result:
                return FilterResult(result=True, context=response.context)
        return FilterResult(result=False)
