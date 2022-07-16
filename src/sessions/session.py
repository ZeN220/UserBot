import logging
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from vkwave.api import APIOptionsRequestContext, API
from vkwave.api.methods._error import ErrorDispatcher
from vkwave.api.token.token import UserSyncSingleToken, BotSyncSingleToken, Token

from src.api import ERROR_HANDLERS, default_error_handler
from src.dispatching import LongPoll

if TYPE_CHECKING:
    from src.dispatching import Dispatcher

logger = logging.getLogger(__name__)


@dataclass
class User:
    owner_id: int
    token: str
    api_context: APIOptionsRequestContext

    @classmethod
    async def create_from_token(
        cls,
        user_token: str,
        error_dispatcher: Optional[ErrorDispatcher] = None
    ) -> 'User':
        if error_dispatcher is None:
            error_dispatcher = ErrorDispatcher()
            error_dispatcher.handlers = ERROR_HANDLERS
            error_dispatcher.set_default_error_handler(default_error_handler)

        token = UserSyncSingleToken(Token(user_token))
        api_context = API(tokens=token, error_dispatcher=error_dispatcher).get_context()

        user_profile = await api_context.users.get()
        owner_id = user_profile.response[0].id

        return cls(
            owner_id=owner_id,
            token=user_token,
            api_context=api_context
        )


@dataclass
class Group:
    api_context: APIOptionsRequestContext

    @classmethod
    def create_from_token(cls, bot_token: str) -> 'Group':
        token = BotSyncSingleToken(Token(bot_token))
        api_context = API(tokens=token).get_context()
        return cls(api_context=api_context)


@dataclass
class Session:
    user: User
    group: Group
    commands_prefix: str
    dispatcher: 'Dispatcher'

    @classmethod
    async def create_from_tokens(
        cls,
        user_token: str,
        bot_token: str,
        commands_prefix: str,
        dispatcher: 'Dispatcher'
    ) -> 'Session':
        user = await User.create_from_token(user_token)
        group = Group.create_from_token(bot_token)
        return cls(
            user=user, group=group, commands_prefix=commands_prefix, dispatcher=dispatcher
        )

    async def close_session(self) -> None:
        await self.user.api_context.api_options.get_client().close()
        await self.group.api_context.api_options.get_client().close()

    async def send_service_message(self, text: str) -> None:
        await self.group.api_context.messages.send(
            peer_id=self.owner_id,
            random_id=0,
            message=text
        )

    async def run_polling(self) -> None:
        longpoll = LongPoll(self)
        await longpoll.start()

    @property
    def owner_id(self) -> int:
        return self.user.owner_id

    def __eq__(self, other_session: 'Session') -> bool:
        return self.user.token == other_session.user.token or self.owner_id == other_session.owner_id
