from typing import List, Optional

from vkwave.api import APIOptionsRequestContext

from .base import Module, CommandResponse, BaseHandler, Priority
from .filters import ParseUserFilter, ConversationFilter
from src.dispatching import UserEvent

social_module = Module('social')


@social_module.register(
    ParseUserFilter(), name='add_friend',
    aliases=['др+', 'друг+', 'fr+', 'friend+'], args_syntax=r'(\d+)?'
)
class AddFriendHandler(BaseHandler):
    async def execute(
        self,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.friends.add(user_id=user_id)
            return CommandResponse(response='[♻] Пользователи успешно добавлены в друзья.')

        await api_context.friends.add(user_id=user_id)
        return CommandResponse(
            response=f'[♻] [id{user_id}|Пользователь] успешно добавлен в друзья.'
        )


@social_module.register(
    ParseUserFilter(), name='remove_friend',
    aliases=['др-', 'друг-', 'fr-', 'friend-'], args_syntax=r'(\d+)?'
)
class RemoveFriendHandler(BaseHandler):
    async def execute(
        self,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.friends.delete(user_id=user_id)
            return CommandResponse(response='[♻] Пользователи успешно удалены из списка друзей.')

        await api_context.friends.delete(user_id=user_id)
        return CommandResponse(
            response=f'[♻] [id{user_id}|Пользователь] успешно удален из списка друзей.'
        )


@social_module.register(
    ParseUserFilter(), name='add_block',
    aliases=['чс+', 'блок+', 'bl+', 'block+'], args_syntax=r'(\d+)?'
)
class AddBlockHandler(BaseHandler):
    async def execute(
        self,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.account.ban(owner_id=user_id)
            return CommandResponse(response='[💣] Пользователи успешно добавлены в черный список.')

        await api_context.account.ban(owner_id=user_id)
        return CommandResponse(
            response=f'[💣] [id{user_id}|Пользователь] успешно добавлен в черный список.'
        )


@social_module.register(
    ParseUserFilter(), name='remove_block',
    aliases=['чс-', 'блок-', 'bl-', 'block-'], args_syntax=r'(\d+)?'
)
class RemoveBlockHandler(BaseHandler):
    async def execute(
        self,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.account.unban(owner_id=user_id)
            return CommandResponse(response='[💣] Пользователи успешно удалены из черного списка.')

        await api_context.account.unban(owner_id=user_id)
        return CommandResponse(
            response=f'[💣] [id{user_id}|Пользователь] успешно удален из черного списка.'
        )
