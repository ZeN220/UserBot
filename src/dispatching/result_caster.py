from typing import Type, Any, Callable, Awaitable, Dict
import logging

from vkwave.bots.core.dispatching.dp import BaseResultCaster

from src.commands import CommandResponse
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


async def none_caster(_, event: UserEvent):  # noqa
    pass


async def command_response_caster(command_response: CommandResponse, event: UserEvent):
    session = event.session
    response = command_response.response
    for index in range(0, len(response), 4096):
        await session.send_service_message(response[index:index + 4096])


CASTERS = {
    type(None): none_caster,
    CommandResponse: command_response_caster
}
