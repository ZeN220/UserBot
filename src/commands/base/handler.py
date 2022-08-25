from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Tuple, Optional, Dict, Any
import inspect

from src.dispatching import UserEvent
from src.services import HolderGateway
from .errors import NotEnoughArgs
from .types import CommandArgs, CommandResponse

if TYPE_CHECKING:
    from .command import Command


class BaseHandler(ABC):
    def __init__(self, command: 'Command'):
        self.command = command
        self.handler_args = inspect.getfullargspec(self.execute)

    @abstractmethod
    async def execute(self, **kwargs) -> 'CommandResponse':
        ...

    async def run(self, event: UserEvent, **kwargs) -> Optional['CommandResponse']:
        filters_result, context = await self.check_filters(event)
        if not filters_result:
            return

        if self.command.args_syntax:
            command_args = self.parse_args(event.object.object.text)
            if not command_args:
                raise NotEnoughArgs(self.command.name, event.session.owner_id)
            context.update(command_args.args)
        kwargs = self._prepare_kwargs(kwargs)
        context.update(kwargs)
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

    def _prepare_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value for key, value in kwargs.items() if key in self.handler_args.args
        }
