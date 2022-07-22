import logging
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type, Union

from src.database import Module
from .command import Command

if TYPE_CHECKING:
    import re
    
    from src.dispatching import UserEvent
    from src.dispatching.filters import BaseFilter
    from src.sessions import Session
    from .handler import BaseHandler

logger = logging.getLogger(__name__)


class CommandManager:
    commands: List[Command] = []
    modules: List[str] = []
    commands_sessions: Dict['Session', List[Command]] = {}

    @classmethod
    def add_command(cls, command: Command, session: 'Session') -> None:
        session_commands = cls.commands_sessions.get(session)
        session_commands.append(command)
        cls.commands_sessions.update({
            session: session_commands
        })
        logger.debug(f'Команда {command.name} для сессии [{session.owner_id}] успешно инициализирована.')
        
    @classmethod
    def register(
        cls,
        name: str,
        module: str,
        aliases: List[str],
        priority: int,
        pattern: Union[str, 're.Pattern'],
        filters: Optional[List['BaseFilter']] = None,
    ):
        def decorator(handler: Type['BaseHandler']):
            command = Command(
                name=name, module=module, aliases=aliases,
                priority=priority, pattern=pattern, filters=filters,
                handler=handler
            )
            cls.commands.append(command)
            return command
        return decorator

    @classmethod
    async def find_command(cls, event: 'UserEvent') -> Optional[Tuple[Command, dict]]:
        session = event.session
        commands = cls.commands_sessions[session]
        for command in commands:
            result = await command.is_suitable(event)
            if result:
                return command, result

    @classmethod
    def setup_commands(cls):
        start_time = time.time()
        import src.commands # noqa
        end_time = time.time()
        result = round(end_time - start_time, 3)
        logger.info(f'Команды успешно инициализированы за {result} секунд.')

    @classmethod
    async def setup_commands_session(cls, session: 'Session', modules: Optional[List[str]] = None):
        start_time = time.time()
        if modules is None:
            modules = await Module.get_activate_modules(session)

        for module in modules:
            # Фильтрация команд для получения только тех, чьи модули включены в сессии
            commands = filter(lambda command: command.module == module, cls.commands)
            for session_command in commands:
                cls.add_command(session_command, session)
        end_time = time.time()
        result = round(end_time - start_time, 3)
        logger.info(f'Команды для сессии [{session.owner_id}] успешно инициализированы за {result} секунд.')
