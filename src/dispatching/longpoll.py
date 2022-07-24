import asyncio
import logging
import traceback
from typing import TYPE_CHECKING, Optional

from vkwave.bots.core.dispatching.extensions import UserLongpoll
from vkwave.longpoll import UserLongpollData

if TYPE_CHECKING:
    from src.sessions import Session

logger = logging.getLogger(__name__)


class LongPoll:
    def __init__(self, session: 'Session'):
        self.session = session
        self.dispatcher = self.session.dispatcher
        self.longpoll = UserLongpoll(
            api=self.session.user.api_context, bot_longpoll_data=UserLongpollData()
        )

    async def _start(self):
        loop = asyncio.get_running_loop()
        logger.debug(f'LongPoll для сессии [{self.session.owner_id}] успешно запущен.')
        while True:
            try:
                events = await self.longpoll.get_updates()
                for event in events:
                    loop.create_task(
                        self.dispatcher.process_event(event, self.session)
                    )
            except Exception as e:
                logger.error(f"Error in Longpoll ({e}): {traceback.format_exc()}")
                continue

    async def start(self) -> asyncio.Task:
        loop = asyncio.get_running_loop()
        task = loop.create_task(self._start(), name=str(self.session.owner_id))
        return task
