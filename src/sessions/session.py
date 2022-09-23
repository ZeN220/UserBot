import logging
from typing import Optional, List, Dict

from pydantic import BaseModel
from vkwave.api import APIOptionsRequestContext, API
from vkwave.api.methods._error import ErrorDispatcher, APIError
from vkwave.api.token.token import UserSyncSingleToken, BotSyncSingleToken, Token

from src.api import ERROR_HANDLERS, default_error_handler, GROUP_ERROR_HANDLERS
from src.dispatching import LongPoll, Dispatcher
from .errors import InvalidSessionError

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    'logger': {
        'delete_notify': True,
        'edit_notify': False
    },
    'to_delete': {
        'trigger': ['дд'],
        'argument': '-'
    }
}


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
        api = API(tokens=token)
        api_context = api.get_context()

        try:
            user_profile = await api_context.users.get()
        except APIError as error:
            if error.code == 5:
                await api.default_api_options.get_client().close()
                raise InvalidSessionError(user_token)
            else:
                raise APIError(error.code, error.message, error.request_params)

        else:
            owner_id = user_profile.response[0].id
            api.default_api_options.error_dispatcher = error_dispatcher

            return cls(
                owner_id=owner_id,
                token=user_token,
                api_context=api.get_context()
            )

    class Config:
        arbitrary_types_allowed = True
        copy_on_model_validation = False


class Group(BaseModel):
    group_id: int
    group_token: str
    api_context: APIOptionsRequestContext

    @classmethod
    async def create_from_token(
        cls, group_token: str, error_dispatcher: Optional['ErrorDispatcher'] = None
    ) -> 'Group':
        if error_dispatcher is None:
            error_dispatcher = ErrorDispatcher()
            error_dispatcher.handlers = GROUP_ERROR_HANDLERS
            error_dispatcher.set_default_error_handler(default_error_handler)

        token = BotSyncSingleToken(Token(group_token))
        api_context = API(tokens=token, error_dispatcher=error_dispatcher).get_context()
        result = await api_context.groups.get_by_id()
        return cls(api_context=api_context, group_token=group_token, group_id=result.response[0].id)

    class Config:
        arbitrary_types_allowed = True
        copy_on_model_validation = False


class Session(BaseModel):
    user: User
    group: Group
    commands_prefix: str
    deactivate_modules: List[str] = []
    delete_command_after: Optional[bool] = True
    settings: Dict[str, dict]

    @classmethod
    async def create_from_tokens(
        cls,
        user_token: str,
        group_token: str,
        commands_prefix: str,
        deactivate_modules: Optional[List[str]] = None,
        delete_command_after: bool = True,
        settings: Optional[Dict[str, dict]] = None
    ) -> 'Session':
        user = await User.create_from_token(user_token)
        group = await Group.create_from_token(group_token)
        deactivate_modules = deactivate_modules or []
        settings = settings or DEFAULT_SETTINGS
        return cls(
            user=user, group=group, commands_prefix=commands_prefix,
            delete_command_after=delete_command_after, deactivate_modules=deactivate_modules,
            settings=settings
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

    async def run_polling(self, dispatcher: Dispatcher) -> None:
        # TODO: Создание объекта Longpoll в этом месте не лучшее решение
        longpoll = LongPoll(session=self, dispatcher=dispatcher)
        await longpoll.start()

    @property
    def owner_id(self) -> int:
        return self.user.owner_id

    def __hash__(self) -> int:
        return hash(self.user.token)

    def __eq__(self, other_session: 'Session') -> bool:
        return (
            self.user.token == other_session.user.token
            or self.owner_id == other_session.owner_id
        )

    class Config:
        arbitrary_types_allowed = True
