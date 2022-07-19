from typing import TYPE_CHECKING

from vkwave.bots import UserEvent as VKWaveUserEvent
from vkwave.api import APIOptionsRequestContext
from vkwave.types.user_events import BaseUserEvent

if TYPE_CHECKING:
    from src.sessions import Session


class UserEvent(VKWaveUserEvent):
    def __init__(self, object_: BaseUserEvent, session: 'Session'):
        super().__init__(object=object_, api_ctx=session.user.api_context)
        self.session = session
