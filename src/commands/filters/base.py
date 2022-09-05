from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from src.dispatching import UserEvent


class FilterResult(BaseModel):
    result: bool = Field(None, description='Result of checking filter')
    context: dict = Field({}, description='Values from filter')


class BaseFilter(ABC):
    @abstractmethod
    async def check(self, event: UserEvent) -> FilterResult:
        ...

    def __or__(self, other: 'BaseFilter'):
        return OrFilter(self, other)

    def __invert__(self):
        return NotFilter(self)


class OrFilter(BaseFilter):
    def __init__(self, *filters: BaseFilter):
        self.filters = filters

    async def check(self, event: UserEvent) -> FilterResult:
        for filter_ in self.filters:
            response = await filter_.check(event)
            if response.result:
                return FilterResult(result=True, context=response.context)
        return FilterResult(result=False)


class NotFilter(BaseFilter):
    def __init__(self, filter_: BaseFilter):
        self.filter_ = filter_

    async def check(self, event: UserEvent) -> FilterResult:
        response = await self.filter_.check(event)
        return FilterResult(result=not response.result, context=response.context)
