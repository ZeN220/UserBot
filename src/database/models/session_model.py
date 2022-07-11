from typing import List

from tortoise import Model, fields

from src.sessions import Session


class SessionModel(Model):
    owner_id = fields.IntField(pk=True)
    user_token = fields.TextField()
    bot_token = fields.TextField()
    commands_prefix = fields.CharField(max_length=16)

    async def create_session(self) -> Session:
        session = await Session.create_from_tokens(
            user_token=self.user_token,
            bot_token=self.bot_token,
            commands_prefix=self.commands_prefix
        )
        return session

    @classmethod
    async def create_all_sessions(cls) -> List[Session]:
        result = []
        sessions = await cls.all()
        for session in sessions:
            session = await session.create_session()
            result.append(session)
        return result

    class Meta:
        table = 'sessions'
