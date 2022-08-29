from vkwave.bots import MiddlewareResult, BaseMiddleware
from sqlalchemy.orm import sessionmaker

from src.dispatching import UserEvent
from src.services import HolderGateway


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool: sessionmaker):
        self.session_pool = session_pool

    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        session = self.session_pool()
        event['session'] = session
        event['gateway'] = HolderGateway(session)
        return MiddlewareResult(True)

    async def post_process_event(self, event: UserEvent):
        await event['session'].close()
