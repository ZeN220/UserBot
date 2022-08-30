from typing import List

from src.dispatching import UserEvent
from .base import BaseFilter, FilterResult


class FilterManager:
    def __init__(self, filters: List[BaseFilter]):
        self.filters = filters

    def add_filter(self, filter_: BaseFilter):
        self.filters.append(filter_)

    async def check_filters(self, event: UserEvent) -> FilterResult:
        context = {}
        for filter_ in self.filters:
            response = await filter_.check(event)
            if response.result:
                context.update(response.context)
                continue
            return FilterResult(result=False, context={})
        return FilterResult(result=True, context=context)
