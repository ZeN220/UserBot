from dataclasses import dataclass

from vkwave.api.token.token import UserSyncSingleToken, BotSyncSingleToken, Token
from vkwave.api import APIOptionsRequestContext, API


@dataclass
class User:
    owner_id: int
    token: str
    api_context: APIOptionsRequestContext

    @classmethod
    async def create_from_token(cls, user_token: str) -> 'User':
        token = UserSyncSingleToken(Token(user_token))
        api_context = API(tokens=token).get_context()

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

    @classmethod
    async def create_from_tokens(
        cls,
        user_token: str,
        bot_token: str,
        commands_prefix: str,
    ) -> 'Session':
        user = await User.create_from_token(user_token)
        group = Group.create_from_token(bot_token)
        return cls(user=user, group=group, commands_prefix=commands_prefix)

    async def close_session(self) -> None:
        await self.user.api_context.api_options.get_client().close()
        await self.group.api_context.api_options.get_client().close()

    @property
    def owner_id(self) -> int:
        return self.user.owner_id

    def __eq__(self, other_session: 'Session') -> bool:
        return self.user.token == other_session.user.token or self.owner_id == other_session.owner_id
