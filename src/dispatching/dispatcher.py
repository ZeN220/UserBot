import logging
from typing import List, NewType, Optional, cast, TYPE_CHECKING

from vkwave.api import APIOptionsRequestContext
from vkwave.bots.core.dispatching.dp.middleware.middleware import MiddlewareManager
from vkwave.bots.core.dispatching.dp.result_caster import BaseResultCaster
from vkwave.bots.core.dispatching.events.raw import ExtensionEvent
from vkwave.bots.core.dispatching.router.router import HANDLER_NOT_FOUND, BaseRouter
from vkwave.types.user_events import get_event_object

if TYPE_CHECKING:
    from src.sessions import Session
from .event import UserEvent

ProcessingResult = NewType("ProcessingResult", bool)

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(
        self,
        api_context: APIOptionsRequestContext,
        session: 'Session',
        result_caster: Optional[BaseResultCaster] = None
    ):
        self.api_context = api_context
        self.session = session
        self.middleware_manager = MiddlewareManager()
        self.routers: List[BaseRouter] = []
        self.result_caster: BaseResultCaster = result_caster

    def add_router(self, router: BaseRouter):
        self.routers.append(router)

    async def process_event(
        self, raw_event: list
    ) -> ProcessingResult:
        logger.debug(f"New event! Raw:\n{raw_event}")

        raw_event = cast(list, raw_event)
        obj = get_event_object(raw_event)
        event = UserEvent(obj, self.api_context, self.session)
        print(event)

        logger.debug(f"New event! Formatted:\n{event}")

        if not await self.middleware_manager.execute_pre_process_event(event):
            return ProcessingResult(False)
        for router in self.routers:
            if await router.is_suitable(event):
                result = await router.process_event(event)
                if result is HANDLER_NOT_FOUND:
                    continue
                await self.result_caster.cast(result, event)
                logger.debug("Event was successfully handled")

                await self.middleware_manager.execute_post_process_event(event)
                return ProcessingResult(True)
        logger.debug("Event wasn't handled")
        await self.middleware_manager.execute_post_process_event(event)
        return ProcessingResult(False)
