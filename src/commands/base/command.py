import re
from typing import List, TYPE_CHECKING, Type, Union, Optional

from src.commands.filters.base import BaseFilter
from src.dispatching import UserEvent
from .types import CommandResponse
from .errors import NotEnoughArgs
from src.commands.filters.errors import ParseUserError

if TYPE_CHECKING:
    from .handler import BaseHandler


class Command:
    def __init__(
        self,
        *filters: BaseFilter,
        name: str,
        aliases: List[str],
        handler: Type['BaseHandler'],
        priority: int = 50,
        args_syntax: Optional[Union[str, List[str]]] = None,
    ):
        self.name = name
        self.aliases = aliases
        self.filters = filters or []
        self.handler = handler(command=self)
        self.priority = priority
        if isinstance(args_syntax, list):
            self.args_syntax = [re.compile(syntax) for syntax in args_syntax]
        else:
            self.args_syntax = [re.compile(args_syntax)] if args_syntax is not None else []

    def check_aliases(self, text: str) -> bool:
        return text.startswith(tuple(self.aliases))

    def is_suitable(self, text: str) -> bool:
        is_command = self.check_aliases(text)
        return is_command

    async def start(self, event: 'UserEvent', **kwargs) -> CommandResponse:
        try:
            response = await self.handler.run(event=event, **kwargs)
        except ParseUserError:
            response = CommandResponse(
                code=404, 
                response=f'[⚠] При обработке команды «{self.name}» не удалось '
                         f'получить пользователя на которого она будет воздействовать.'
            )
        except NotEnoughArgs:
            response = CommandResponse(
                code=400,
                response=f'[⚠] При написании команды «{self.name}» '
                         f'было указано недостаточно аргументов.'
            )
        return response
