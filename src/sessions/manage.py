from typing import List, Optional, TYPE_CHECKING, NoReturn, Union
import logging
import asyncio

from src.dispatching import LongPoll
from .errors import UndefinedSessionError

if TYPE_CHECKING:
    from .session import Session

logger = logging.getLogger(__name__)


class SessionManager:
    main_session: Optional['Session'] = None
    sessions: List['Session'] = []

    @classmethod
    def is_duplicate(cls, other_session: 'Session') -> bool:
        for session in cls.sessions:
            if session == other_session:
                return True
        return cls.main_session and cls.main_session == other_session

    @classmethod
    def get_session_from_token(cls, user_token: str) -> Union[NoReturn, 'Session']:
        for session in cls.sessions:
            if session.user.token == user_token:
                return session
        raise UndefinedSessionError(f'Session with access token {user_token} is undefined')

    @classmethod
    def add_session(cls, session: 'Session', is_main: Optional[bool] = False) -> None:
        duplicate = cls.is_duplicate(session)
        if duplicate:
            logger.warning(f'Сессия [{session.owner_id}] игнорируется из-за имеющегося дубликата')
            return

        if not is_main:
            cls.sessions.append(session)
            logger.info(f'Сессия [{session.owner_id}] успешно инициализирована.')
            return
        elif is_main and not cls.main_session:
            cls.main_session = session
            logger.info(f'Сессия [{session.owner_id}] успешно инициализирована как основная.')
            return

        logger.info(
            f'Основная сессия [{cls.main_session.owner_id}] уже инициализирована, '
            f'поэтому [{session.owner_id}] игнорируется.'
        )

    @classmethod
    def add_many_sessions(cls, sessions: List['Session']) -> None:
        for session in sessions:
            cls.add_session(session)

    @classmethod
    def delete_session(cls, session: 'Session') -> None:
        cls.sessions.remove(session)
        logger.info(f'Сессия [{session.owner_id}] была успешно удалена.')

    @classmethod
    async def run_all_polling(cls) -> None:
        loop = asyncio.get_running_loop()
        if cls.main_session:
            loop.create_task(cls.main_session.run_polling())
        for session in cls.sessions:
            loop.create_task(session.run_polling())

    @classmethod
    async def close_sessions(cls) -> None:
        if cls.main_session:
            await cls.main_session.close_session()
        for session in cls.sessions:
            await session.close_session()
