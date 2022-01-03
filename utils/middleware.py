from vkwave.bots import (
    MiddlewareResult,
    BaseMiddleware,
    UserEvent
)


class Middleware(BaseMiddleware):
    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        if event.object is None:
            return MiddlewareResult(False)
        needed_events: set = {event.object.object.event_id} & {4, 5, 2}
        return MiddlewareResult(not not needed_events)
