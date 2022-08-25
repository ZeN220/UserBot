import re
from typing import List, TYPE_CHECKING, Type, Union

from src.dispatching import UserEvent
from src.services import HolderGateway
from .filters import BaseFilter
from .types import CommandResponse

if TYPE_CHECKING:
    from .handler import BaseHandler


class Command:
    def __init__(
        self,
        *filters: BaseFilter,
        name: str,
        module: str,
        aliases: List[str],
        handler: Type['BaseHandler'],
        priority: int,
        args_syntax: Union[str, List[str]],
    ):
        self.name = name
        self.module = module
        self.aliases = aliases
        self.handler = handler
        self.priority = priority
        self.filters = filters
        if isinstance(args_syntax, list):
            self.args_syntax = [re.compile(syntax) for syntax in args_syntax]
        else:
            self.args_syntax = [re.compile(args_syntax)]

    def check_aliases(self, text: str) -> bool:
        return text.startswith(tuple(self.aliases))

    async def is_suitable(self, event: 'UserEvent') -> bool:
        text = event.object.object.text[1:].lstrip()
        is_command = self.check_aliases(text)
        return is_command

    async def start(self, event: 'UserEvent', gateway: HolderGateway) -> 'CommandResponse':
        handler = self.handler(event=event, command=self, gateway=gateway)
        return await handler.run()
