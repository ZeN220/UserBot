from typing import Optional, List

from vkwave.api import APIOptionsRequestContext

from .base import Module, BaseHandler, CommandResponse, Priority
from .filters import ParseUserFilter, ConversationFilter
from src.dispatching import UserEvent

chats_module = Module('chats')


@chats_module.register(
    ParseUserFilter(), ConversationFilter(from_chat=True), name='invite',
    aliases=['invite', 'добавить'], args_syntax=r'(\d+)?'
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


@chats_module.register(
    ParseUserFilter(), ConversationFilter(from_chat=True), name='kick',
    aliases=['kick', 'кик'], priority=Priority.HIGH, args_syntax=r'(\d+)?'
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
                    member_id=user_id, chat_id=chat_id
                )
            return CommandResponse(
                response='[👮] Пользователи успешно исключены из чата.'
            )
        await api_context.messages.remove_chat_user(
            member_id=user_id, chat_id=chat_id
        )

        response = f'[👮] [id{user_id}|Пользователь] успешно исключен из чата.'
        if user_id < 0:
            response = f'[👮] [club{abs(user_id)}|Сообщество] успешно исключено из чата.'
        return CommandResponse(response=response)


@chats_module.register(
    ParseUserFilter(), ConversationFilter(from_chat=True), name='set_admin',
    aliases=['admin+', 'админ+'], args_syntax=r'(\d+)?'
)
class SetAdminHandler(BaseHandler):
    async def execute(
        self,
        event: UserEvent,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> 'CommandResponse':
        peer_id = event.object.object.peer_id
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.api_request(
                    'messages.setMemberRole',
                    {'member_id': user_id, 'role': 'admin', 'peer_id': peer_id}
                )
            return CommandResponse(
                response='[🤵] Пользователи успешно назначены администраторами чата.'
            )
        await api_context.api_request(
            'messages.setMemberRole',
            {'member_id': user_id, 'role': 'admin', 'peer_id': peer_id}
        )

        response = f'[🤵] [id{user_id}|Пользователь] успешно назначен администратором чата.'
        if user_id < 0:
            response = (
                f'[🤵] [club{abs(user_id)}|Сообщество] '
                f'успешно назначено администратором чата.'
            )
        return CommandResponse(response=response)


@chats_module.register(
    ParseUserFilter(), ConversationFilter(from_chat=True), name='remove_admin',
    aliases=['admin-', 'админ-'], args_syntax=r'(\d+)?'
)
class SetAdminHandler(BaseHandler):
    async def execute(
        self,
        event: UserEvent,
        api_context: APIOptionsRequestContext,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> 'CommandResponse':
        peer_id = event.object.object.peer_id
        if users_ids is not None:
            for user_id in users_ids:
                await api_context.api_request(
                    'messages.setMemberRole',
                    {'member_id': user_id, 'role': 'member', 'peer_id': peer_id}
                )
            return CommandResponse(
                response='[👷] С пользователей успешно сняты права администратора.'
            )
        await api_context.api_request(
            'messages.setMemberRole',
            {'member_id': user_id, 'role': 'member', 'peer_id': peer_id}
        )

        response = f'[👷] С [id{user_id}|пользователь] успешно сняты права администратора чата.'
        if user_id < 0:
            response = (
                f'[👷] С [club{abs(user_id)}|сообщества] '
                f'успешно сняты права администратора чата.'
            )
        return CommandResponse(response=response)
