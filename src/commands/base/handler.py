from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple, Optional

from src.dispatching import UserEvent
from src.services import HolderGateway
from .errors import NotEnoughArgs
from .types import CommandArgs, CommandResponse

if TYPE_CHECKING:
    from .command import Command


class BaseHandler(ABC):
    def __init__(self, event: UserEvent, command: 'Command', gateway: HolderGateway):
        self.event = event
        self.command = command
        self.gateway = gateway

    @abstractmethod
    async def execute(self, **kwargs) -> 'CommandResponse':
        ...

    async def run(self) -> Optional['CommandResponse']:
        filters_result, context = await self.check_filters(self.event)
        if not filters_result:
            return

        if self.command.args_syntax:
            command_args = self.parse_args(self.event.object.object.text)
            if not command_args:
                raise NotEnoughArgs(self.command.name, self.event.session.owner_id)
            context.update(command_args.args)
        return await self.execute(**context)

    async def check_filters(self, event: 'UserEvent') -> Tuple[bool, dict]:
        context = {}
        for filter_ in self.command.filters:
            response = await filter_.check(event, self.command)
            if response.result:
                context.update(response.context)
                continue
            return False, {}
        return True, context

    def parse_args(self, text: str) -> Optional[CommandArgs]:
        patterns = self.command.args_syntax
        for pattern in patterns:
            args = pattern.search(text)
            if args is None:
                continue
            args = CommandArgs(args=args.groupdict())
            return args
        return
