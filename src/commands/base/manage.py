import logging
import time
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Type, Union

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
    async def find_command(cls, event: 'UserEvent') -> Tuple[Optional[Command], dict]:
        session = event.session
        commands = cls.commands_sessions[session]
        for command in commands:
            result, context = await command.is_suitable(event)
            if result:
                return command, context
        return None, {}

    @classmethod
    def setup_commands(cls):
        start_time = time.time()
        import src.commands # noqa
        end_time = time.time()
        result = round(end_time - start_time, 3)
        logger.info(f'Команды успешно инициализированы за {result} секунд.')

    @classmethod
    async def setup_commands_session(cls, session: 'Session'):
        start_time = time.time()
        for session_command in cls.commands:
            command_module = session_command.module
            is_activate_module = session.modules.get(command_module)
            if is_activate_module:
                cls.add_command(session_command, session)
            elif is_activate_module is None:
                logger.warning(f'В сессии [{session.owner_id}] не указан модуль «{command_module}». Отредактируйте файл sessions.toml и добавьте его в список модулей.')

        end_time = time.time()
        result = round(end_time - start_time, 3)
        logger.info(f'Команды для сессии [{session.owner_id}] успешно инициализированы за {result} секунд.')
