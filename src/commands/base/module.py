from typing import List, Optional, Type, Union

from src.commands.filters.base import BaseFilter
from .command import Command
from .handler import BaseHandler


class Module:
    def __init__(self, name: str):
        self.commands: List[Command] = []
        self.name = name

    def add_command(self, command: Command):
        self.commands.append(command)

    def register(
        self,
        *filters: BaseFilter,
        name: str,
        aliases: List[str],
        priority: int = 50,
        args_syntax: Optional[Union[str, List[str]]] = None,
    ):
        def decorator(handler: Type[BaseHandler]):
            command = Command(*filters, name=name, aliases=aliases, handler=handler,
                              priority=priority, args_syntax=args_syntax)
            self.add_command(command)
            return command
        return decorator

    def get_command(self, text: str) -> Optional[Command]:
        for command in self.commands:
            result = command.is_suitable(text)
            if result:
                return command
        return
