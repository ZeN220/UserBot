from typing import Type, Any, Callable, Awaitable, Dict
import logging

from vkwave.bots.core.dispatching.dp import BaseResultCaster

from .event import UserEvent

logger = logging.getLogger(__name__)

Caster = Callable[[Any, UserEvent], Awaitable[None]]


class ResultCaster(BaseResultCaster):
    def __init__(self):
        # TODO: Сделать отдельную структуру данных для кастеров
        self.casters: Dict[Type[Any], Caster] = {}

    def add_caster(self, typeof: Type[Any], handler: Caster):
        self.casters[typeof] = handler

    async def cast(self, result: Any, event: UserEvent):
        typeof = type(result)
        handler = self.casters.get(typeof)
        if not handler:
            logger.warning("implementation for this type doesn't exist")
            return
        await handler(result, event)


async def none_caster(none_value, event: UserEvent):
    pass


async def command_response_caster(command_response: 'CommandResponse', event: UserEvent):
    """
    TODO: Написать реализацию для CommandResponse
    """
