from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Dict, Any
import inspect
import re

from src.dispatching import UserEvent
from .errors import NotEnoughArgs
from .types import CommandArgs, CommandResponse
from src.commands.filters import FilterManager

if TYPE_CHECKING:
    from .command import Command

# TEXT_WITHOUT_COMMAND создан для удаления префикса и команды из текста сообщения
TEXT_WITHOUT_COMMAND_REGEXP = re.compile(r'^\S+(\s)?')


class BaseHandler(ABC):
    def __init__(self, command: 'Command'):
        self.command = command
        self.handler_args = inspect.getfullargspec(self.execute)
        self.filter_manager = FilterManager(list(self.command.filters))

    @abstractmethod
    async def execute(self, **kwargs) -> 'CommandResponse':
        ...

    async def run(self, event: UserEvent, **kwargs) -> Optional['CommandResponse']:
        filters_response = await self.filter_manager.check_filters(event)
        if not filters_response.result:
            return
        context = filters_response.context

        if self.command.args_syntax:
            text = event.object.object.text[1:].lstrip()
            arguments = TEXT_WITHOUT_COMMAND_REGEXP.sub('', text)
            command_args = self.parse_args(arguments)
            if not command_args:
                raise NotEnoughArgs(self.command.name, event.session.owner_id)
            context.update(command_args.args)

        context.update({'event': event})
        context.update(kwargs)
        context = self._prepare_kwargs(context)

        return await self.execute(**context)

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
