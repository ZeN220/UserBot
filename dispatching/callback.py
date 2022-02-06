from traceback import format_exc
import typing

from vkwave.bots.core.dispatching.handler.callback import BaseCallback
from vkwave.bots.core.dispatching.handler import callback_caster
from vkwave.bots import UserEvent, SimpleUserEvent
from vkwave.api.methods._error import APIError

from utils import bot, config, error_logger


class Callback(BaseCallback):
    def __init__(
        self,
        func: typing.Callable,
    ):
        self.func = func
        self.cast_func = callback_caster.cast(self.func)

    async def execute(self, event: UserEvent) -> typing.Any:
        new_event = SimpleUserEvent(event)
        try:
            return await self.cast_func.execute(new_event)

        except APIError:
            pass

        except Exception as exc:
            error_logger.error(f'{new_event}\n{format_exc()}')

            await bot.api_context.messages.send(
                message=f'При выполнении функции {self.func} произошла ошибка:\n{exc}'
                        f'\nБолее подробная информация указана в logs/errors.log',
                peer_id=config['VK']['user_id'],
                random_id=0
            )
