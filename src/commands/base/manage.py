import logging
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union

from .command import Command
from .filters import BaseFilter

if TYPE_CHECKING:
    from src.dispatching import UserEvent
    from src.sessions import Session
    from .handler import BaseHandler

logger = logging.getLogger(__name__)


class CommandManager:
    commands: List[Command] = []
    commands_sessions: Dict['Session', List[Command]] = {}

    @classmethod
    def add_command(cls, command: Command, session: 'Session') -> None:
        session_commands = cls.commands_sessions.get(session, [])
        session_commands.append(command)
        cls.commands_sessions.update({
            session: session_commands
        })
        logger.debug(f'Команда {command.name} для сессии [{session.owner_id}] успешно инициализирована.')
        
    @classmethod
    def register(
        cls,
        *filters: BaseFilter,
        name: str,
        module: str,
        aliases: List[str],
        priority: int,
        args_syntax: Union[str, List[str]],
    ):
        def decorator(handler: Type['BaseHandler']):
            command = Command(
                name=name, module=module, aliases=aliases,
                priority=priority, args_syntax=args_syntax, handler=handler,
                *filters
            )
            cls.commands.append(command)
            return command
        return decorator

    @classmethod
    async def find_command(cls, event: 'UserEvent') -> Optional[Command]:
        session = event.session
        for command in cls.commands:
            if command.module in session.deactivate_modules:
                continue
            result = await command.is_suitable(event)
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
