from typing import List, Optional
import logging

from .session import Session

logger = logging.getLogger(__name__)


class SessionManager:
    main_session: Optional[Session] = None
    sessions: List[Session] = []

    @classmethod
    def is_duplicate(cls, other_session: Session) -> bool:
        for session in cls.sessions:
            if session == other_session:
                return True
        return cls.main_session and cls.main_session == other_session

    @classmethod
    def add_session(cls, session: Session, is_main: Optional[bool] = False) -> None:
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
    async def close_sessions(cls) -> None:
        await cls.main_session.close_session()
        for session in cls.sessions:
            await session.close_session()
