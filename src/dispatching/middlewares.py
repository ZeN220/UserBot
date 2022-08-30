import html

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


class EnvironmentMiddleware(BaseMiddleware):
    def __init__(self, **kwargs):
        self.environment = kwargs

    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        event.user_data.update(self.environment)
        return MiddlewareResult(True)


class TextShieldingMiddleware(BaseMiddleware):
    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        text = event.object.dict().get('object').get('text')
        if text is not None:
            event.object.object.text = html.unescape(text)
        return MiddlewareResult(True)
