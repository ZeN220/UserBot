import logging
import time
from typing import TYPE_CHECKING, List, Optional, Type, Union

from src.sessions import Session
from .command import Command
from src.commands.filters.base import BaseFilter

if TYPE_CHECKING:
    from .handler import BaseHandler

logger = logging.getLogger(__name__)


class CommandManager:
    commands: List[Command] = []

    @classmethod
    def add_command(cls, command: Command):
        cls.commands.append(command)
        
    @classmethod
    def register(
        cls,
        *filters: BaseFilter,
        name: str,
        module: str,
        aliases: List[str],
        priority: int,
        args_syntax: Optional[Union[str, List[str]]] = None,
    ):
        def decorator(handler: Type['BaseHandler']):
            command = Command(
                name=name, module=module, aliases=aliases,
                priority=priority, args_syntax=args_syntax, handler=handler,
                *filters
            )
            cls.add_command(command)
            return command
        return decorator

    @classmethod
    def find_command(cls, session: Session, text: str) -> Optional[Command]:
        for command in cls.commands:
            if command.module in session.deactivate_modules:
                continue
            result = command.is_suitable(text)
            if result:
                return command
        return

    @classmethod
    def setup_commands(cls):
        start_time = time.time()
        import src.commands # noqa
        cls.commands.sort(key=lambda command: command.priority)
        end_time = time.time()
        result = round(end_time - start_time, 3)
        logger.info(f'Команды успешно инициализированы за {result} секунд.')


# Алиас
command_manager = CommandManager
