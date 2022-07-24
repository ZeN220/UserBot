import logging
from typing import Optional, Dict

from vkwave.api import APIOptionsRequestContext, API
from vkwave.api.methods._error import ErrorDispatcher
from vkwave.api.token.token import UserSyncSingleToken, BotSyncSingleToken, Token
from pydantic import BaseModel

from src.api import ERROR_HANDLERS, default_error_handler
from src.dispatching import LongPoll, Dispatcher

logger = logging.getLogger(__name__)


class User(BaseModel):
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

    class Config:
        arbitrary_types_allowed = True
        copy_on_model_validation = False


class Group(BaseModel):
    api_context: APIOptionsRequestContext

    @classmethod
    def create_from_token(cls, bot_token: str) -> 'Group':
        token = BotSyncSingleToken(Token(bot_token))
        api_context = API(tokens=token).get_context()
        return cls(api_context=api_context)

    class Config:
        arbitrary_types_allowed = True
        copy_on_model_validation = False


class Session(BaseModel):
    user: User
    group: Group
    commands_prefix: str
    dispatcher: Dispatcher
    modules: Dict[str, bool]
    delete_command_after: bool

    @classmethod
    async def create_from_tokens(
        cls,
        user_token: str,
        group_token: str,
        commands_prefix: str,
        dispatcher: 'Dispatcher',
        modules: Dict[str, bool],
        delete_command_after: Optional[bool] = True
    ) -> 'Session':
        user = await User.create_from_token(user_token)
        group = Group.create_from_token(group_token)
        return cls(
            user=user, group=group, commands_prefix=commands_prefix,
            dispatcher=dispatcher, delete_command_after=delete_command_after, modules=modules
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

    def __hash__(self):
        return hash(self.user.token)

    def __eq__(self, other_session: 'Session') -> bool:
        return self.user.token == other_session.user.token or self.owner_id == other_session.owner_id

    class Config:
        arbitrary_types_allowed = True
