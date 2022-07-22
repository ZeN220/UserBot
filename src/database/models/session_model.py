from typing import List, TYPE_CHECKING, Union, NoReturn

from tortoise import Model, fields

from src.sessions.errors import UndefinedSessionError
from src.sessions import Session

if TYPE_CHECKING:
    from src.dispatching import Dispatcher


class SessionModel(Model):
    owner_id = fields.IntField(pk=True)
    user_token = fields.TextField()
    bot_token = fields.TextField()
    commands_prefix = fields.CharField(max_length=16)
    delete_command_after = fields.BooleanField(default=True)

    @classmethod
    async def get_model_from_session(cls, session: Session) -> Union['SessionModel', NoReturn]:
        token = session.user.token
        session = await SessionModel.get_or_none(user_token=token)
        if not session:
            raise UndefinedSessionError(token)
        return session

    async def create_session(self, dispatcher: 'Dispatcher', delete_command_after: bool) -> Session:
        session = await Session.create_from_tokens(
            user_token=self.user_token,
            bot_token=self.bot_token,
            commands_prefix=self.commands_prefix,
            dispatcher=dispatcher,
            delete_command_after=delete_command_after
        )
        return session

    @classmethod
    async def create_all_sessions(cls, dispatcher: 'Dispatcher') -> List[Session]:
        result = []
        sessions = await cls.all()
        for session in sessions:
            session = await session.create_session(dispatcher, session.delete_command_after)
            result.append(session)
        return result

    class Meta:
        table = 'sessions'
