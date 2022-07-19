from typing import List

from vkwave.types.user_events import MessageFlag
from vkwave.bots import MiddlewareResult, BaseMiddleware

from src.dispatching import UserEvent
from src.database import Template


class MessageMiddleware(BaseMiddleware):
    def __init__(self, event_ids: List[int]):
        self.events_ids = event_ids

    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        if event.object is None:
            return MiddlewareResult(False)
        event_id = event.object.object.event_id
        return MiddlewareResult(event_id in self.events_ids)


class FromMeMiddleware(BaseMiddleware):
    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        # В списке флагов события последним элементом является сумма всех флагов, поэтому тут используется битовое "И"
        is_from_me = event.object.object.flags[-1] & MessageFlag.OUTBOX.value
        return MiddlewareResult(bool(is_from_me))


MIDDLEWARES = [MessageMiddleware([2, 4, 5]), FromMeMiddleware()]
