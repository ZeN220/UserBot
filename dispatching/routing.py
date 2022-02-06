import typing

from vkwave.bots.core.dispatching.filters import BaseFilter, EventTypeFilter
from vkwave.bots import DefaultRouter
from vkwave.types.user_events import EventId

from dispatching.callback import Callback


class Router(DefaultRouter):
    def __init__(
        self,
        name: str,
        description: str,
        filters: typing.Optional[typing.List[BaseFilter]] = None
    ):
        super().__init__(filters)
        self.name = name
        self.description = description

    def handler(self, *filters: BaseFilter):
        def decorator(func: typing.Callable[..., typing.Any]):
            record = self.registrar.new()
            record.with_filters(*filters)
            record.handle(Callback(func))
            self.registrar.register(record.ready())
            return func

        return decorator

    def message_handler(self, *filters: BaseFilter):
        def decorator(func: typing.Callable[..., typing.Any]):
            record = self.registrar.new()
            record.with_filters(*filters)
            record.filters.append(EventTypeFilter(EventId.MESSAGE_EVENT.value))
            record.handle(Callback(func))
            self.registrar.register(record.ready())
            return func

        return decorator
