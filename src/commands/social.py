from typing import List, Optional

from vkwave.api import APIOptionsRequestContext

from .base import command_manager, CommandResponse, BaseHandler, Priority
from .filters import ParseUserFilter, ConversationFilter
from src.dispatching import UserEvent


@command_manager.register(
    ParseUserFilter(), name='add_friend', module='social',
    aliases=['др+', 'друг+', 'fr+', 'friend+'], priority=Priority.MEDIUM, args_syntax=[r'(\d+)', '']
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


@command_manager.register(
    ParseUserFilter(), name='remove_friend', module='social',
    aliases=['др-', 'друг-', 'fr-', 'friend-'], priority=Priority.MEDIUM, args_syntax=[r'(\d+)', '']
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


@command_manager.register(
    ParseUserFilter(), name='add_block', module='social',
    aliases=['чс+', 'блок+', 'bl+', 'block+'], priority=Priority.MEDIUM, args_syntax=[r'(\d+)', '']
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


@command_manager.register(
    ParseUserFilter(), name='remove_block', module='social',
    aliases=['чс-', 'блок-', 'bl-', 'block-'], priority=Priority.MEDIUM, args_syntax=[r'(\d+)', '']
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


@command_manager.register(
    ParseUserFilter(), ConversationFilter(from_chat=True), name='invite', module='social',
    aliases=['invite', 'добавить'], args_syntax=[r'(\d+)', ''], priority=Priority.MEDIUM
)
class InviteHandler(BaseHandler):
    async def execute(
        self,
        event: UserEvent,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> 'CommandResponse':
        chat_id = event.object.object.peer_id - 2e9
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.messages.add_chat_user(
                    user_id=user_id, chat_id=chat_id, visible_messages_count=0
                )
            return CommandResponse(
                response='[🏠] Пользователи успешно добавлены в чат.'
            )
        await api_context.messages.add_chat_user(
            user_id=user_id, chat_id=chat_id, visible_messages_count=0
        )
        return CommandResponse(
            response=f'[🏠] [id{user_id}|Пользователь] успешно добавлен в чат.'
        )


@command_manager.register(
    ParseUserFilter(), ConversationFilter(from_chat=True), name='kick', module='social',
    aliases=['kick', 'кик'], priority=Priority.HIGH, args_syntax=[r'(\d+)', '']
)
class KickHandler(BaseHandler):
    async def execute(
        self,
        event: UserEvent,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> 'CommandResponse':
        chat_id = event.object.object.peer_id - 2e9
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.messages.remove_chat_user(
                    user_id=user_id, chat_id=chat_id
                )
            return CommandResponse(
                response='[👮] Пользователи успешно исключены из чата.'
            )
        await api_context.messages.remove_chat_user(
            user_id=user_id, chat_id=chat_id
        )
        return CommandResponse(
            response=f'[👮] [id{user_id}|Пользователь] успешно исключен из чата.'
        )
