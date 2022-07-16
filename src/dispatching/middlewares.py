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


class TemplateMiddleware(BaseMiddleware):
    async def pre_process_event(self, event: UserEvent) -> MiddlewareResult:
        # VK API может вернуть событие с номером 2 в котором может не быть текста сообщения.
        text = event.object.object.dict().get('text')
        if len(text) > 64 or not text:
            return MiddlewareResult(True)

        template = await Template.get_template(trigger=text, owner_id=event.session.owner_id)
        if template:
            await event.api_ctx.messages.edit(
                keep_forward_messages=1, message_id=event.object.object.message_id,
                peer_id=event.object.object.peer_id,
                message=template[0], attachment=template[1]
            )
            return MiddlewareResult(False)
        return MiddlewareResult(True)


MIDDLEWARES = [MessageMiddleware([2, 4, 5]), FromMeMiddleware(), TemplateMiddleware()]
