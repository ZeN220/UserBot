from typing import List, TYPE_CHECKING

from tortoise import Model, fields

from src.sessions import Session

if TYPE_CHECKING:
    from src.dispatching import Dispatcher


class SessionModel(Model):
    owner_id = fields.IntField(pk=True)
    user_token = fields.TextField()
    bot_token = fields.TextField()
    commands_prefix = fields.CharField(max_length=16)

    async def create_session(self, dispatcher: 'Dispatcher') -> Session:
        session = await Session.create_from_tokens(
            user_token=self.user_token,
            bot_token=self.bot_token,
            commands_prefix=self.commands_prefix,
            dispatcher=dispatcher
        )
        return session

    @classmethod
    async def create_all_sessions(cls, dispatcher: 'Dispatcher') -> List[Session]:
        result = []
        sessions = await cls.all()
        for session in sessions:
            session = await session.create_session(dispatcher)
            result.append(session)
        return result

    class Meta:
        table = 'sessions'
