from typing import List, Optional

from .base import command_manager, CommandResponse, BaseHandler, Priority
from .base.filters import ParseUserFilter


@command_manager.register(
    ParseUserFilter(), name='add_friend', module='social',
    aliases=['др+', 'друг+', 'fr+', 'friend+'], priority=Priority.MEDIUM, args_syntax=[r'(\d+)', '']
)
class AddFriendHandler(BaseHandler):
    async def execute(
        self,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await self.event.api_ctx.friends.add(user_id=user_id)
            return CommandResponse(response='[♻] Пользователи успешно добавлены в друзья.')

        await self.event.api_ctx.friends.add(user_id=user_id)
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
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await self.event.api_ctx.friends.delete(user_id=user_id)
            return CommandResponse(response='[♻] Пользователи успешно удалены из списка друзей.')

        await self.event.api_ctx.friends.delete(user_id=user_id)
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
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await self.event.api_ctx.account.ban(owner_id=user_id)
            return CommandResponse(response='[💣] Пользователи успешно добавлены в черный список.')

        await self.event.api_ctx.account.ban(owner_id=user_id)
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
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> CommandResponse:
        if users_ids is not None:
            for user_id in users_ids:
                await self.event.api_ctx.account.unban(owner_id=user_id)
            return CommandResponse(response='[💣] Пользователи успешно удалены из черного списка.')

        await self.event.api_ctx.account.unban(owner_id=user_id)
        return CommandResponse(
            response=f'[💣] [id{user_id}|Пользователь] успешно удален из черного списка.'
        )
