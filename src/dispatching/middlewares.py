from vkwave.bots import MiddlewareResult, BaseMiddleware
from sqlalchemy.orm import sessionmaker

from src.dispatching import UserEvent
from src.services import HolderGateway


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool: sessionmaker):
        self.session_pool = session_pool

    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        session_pool = self.session_pool()
        event['gateway'] = HolderGateway(session_pool)
        return MiddlewareResult(True)
