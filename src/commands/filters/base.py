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


class OrFilter(BaseFilter):
    def __init__(self, *filters: BaseFilter):
        self.filters = filters

    async def check(self, event: UserEvent) -> FilterResult:
        for filter_ in self.filters:
            response = await filter_.check(event)
            if response.result:
                return FilterResult(result=True, context=response.context)
        return FilterResult(result=False)
