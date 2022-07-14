from typing import TYPE_CHECKING

from vkwave.bots.core.dispatching.extensions import UserLongpollExtension, UserLongpoll
from vkwave.longpoll import UserLongpollData

from .dispatcher import Dispatcher
from .result_caster import ResultCaster, none_caster, command_response_caster

if TYPE_CHECKING:
    from src.sessions import Session


class LongPoll:
    def __init__(self, session: 'Session'):
        self.api_context = session.user.api_context

        # TODO: Перенести добавление кастеров в другой модуль
        self.result_caster = ResultCaster()
        self.result_caster.add_caster(type(None), none_caster)
        self.result_caster.add_caster(..., command_response_caster)

        self.dispatcher = Dispatcher(
            api_context=self.api_context, session=session, result_caster=self.result_caster
        )
        self.lp = UserLongpoll(api=self.api_context, bot_longpoll_data=UserLongpollData())
        self.longpoll = UserLongpollExtension(self.dispatcher, self.lp)

    async def run(self):
        await self.longpoll.start()
