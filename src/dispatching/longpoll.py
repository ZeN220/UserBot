import asyncio
import logging
import traceback
from typing import TYPE_CHECKING

from vkwave.bots.core.dispatching.extensions import UserLongpollExtension, UserLongpoll
from vkwave.longpoll import UserLongpollData

from .dispatcher import Dispatcher
from .result_caster import ResultCaster, none_caster, command_response_caster

if TYPE_CHECKING:
    from src.sessions import Session

logger = logging.getLogger(__name__)


class LongPoll:
    def __init__(self, session: 'Session'):
        self.session = session
        self.api_context = self.session.user.api_context

        # TODO: Перенести добавление кастеров в другой модуль
        self.result_caster = ResultCaster()
        self.result_caster.add_caster(type(None), none_caster)
        self.result_caster.add_caster(..., command_response_caster)

        self.dispatcher = Dispatcher(
            api_context=self.api_context, session=session, result_caster=self.result_caster
        )
        self.lp = UserLongpoll(api=self.api_context, bot_longpoll_data=UserLongpollData())
        self.longpoll = UserLongpollExtension(self.dispatcher, self.lp)

    async def start(self):
        loop = asyncio.get_running_loop()
        logger.info(f'LongPoll для сессии [{self.session.owner_id}] успешно запущен.')
        while True:
            try:
                events = await self.lp.get_updates()
                for event in events:
                    print(event)
                    loop.create_task(
                        self.dispatcher.process_event(event)
                    )
            except Exception as e:
                logger.error(f"Error in Longpoll ({e}): {traceback.format_exc()}")
                continue
