from vkwave.api.methods._error import APIError
from vkwave.bots import (
    simple_user_message_handler,
    SimpleUserEvent,
    FromMeFilter,
    MessageFromConversationTypeFilter,
    TextStartswithFilter,
    ReplyMessageFilter,
    TextFilter
)

from utils import get_user_id, send_message_to_me
from dispatching import Router


social_router = Router(
    __name__,
    'Команды направленные на взаимодействия с пользователями.'
)
social_router.registrar.add_default_filter(FromMeFilter(True))


@social_router.message_handler(
    TextStartswithFilter(['.добавить', '.invite', '.пригласить', '.инвайт']),
    MessageFromConversationTypeFilter(from_what='from_chat')
)
async def invite(event: SimpleUserEvent):
    peer_id = event.object.object.peer_id
    user_id = await get_user_id(event)

    try:
        await event.api_ctx.messages.add_chat_user(
            chat_id=peer_id - 2e9,
            user_id=user_id
        )
        await send_message_to_me(
            message=f'[🔧] [id{user_id}|Пользователь] '
                    f'успешно добавлен в беседу.',
        )

    except APIError:
        await send_message_to_me(
            message=f'[🔧] Ошибка! '
                    f'[id{user_id}|Пользователь] '
                    f'либо уже находится в беседе, '
                    f'либо не находится в друзьях.',
        )


@social_router.message_handler(
    MessageFromConversationTypeFilter(from_what='from_chat'),
    TextFilter('+др')
)
async def fr_add(event: SimpleUserEvent):
    user_id = await get_user_id(event)

    try:
        await event.api_ctx.friends.add(user_id=user_id)
        await send_message_to_me(
            message=f'[♻] [id{user_id}|Пользователь] '
                    f'добавлен в друзья.'
        )

    except APIError:
        await send_message_to_me(
            message=f'[💣] [id{user_id}|Пользователь] '
                    f'либо находится в черном списке, '
                    f'либо уже добавлен в друзья.'
        )


@social_router.message_handler(
    MessageFromConversationTypeFilter(from_what='from_chat'),
    TextFilter('+чс')
)
async def block_add(event: SimpleUserEvent):
    user_id = await get_user_id(event)

    try:
        await event.api_ctx.account.ban(owner_id=user_id)
        await send_message_to_me(
            message=f'[💣] [id{user_id}|Пользователь] '
                    f'добавлен в черный список.',
        )

    except APIError:
        await send_message_to_me(
            message=f'[💣] [id{user_id}|Пользователь] '
                    f'уже находится в черном списке.'
        )


@social_router.message_handler(
    MessageFromConversationTypeFilter(from_what='from_chat'),
    ReplyMessageFilter(),
    TextFilter('-др')
)
async def fr_remove(event: SimpleUserEvent):
    user_id = await get_user_id(event)

    await event.api_ctx.friends.delete(user_id=user_id)
    await send_message_to_me(
        message=f'[♻] [id{user_id}|Пользователь] удален из друзей.'
    )


@social_router.message_handler(
    MessageFromConversationTypeFilter(from_what='from_chat'),
    TextFilter('-чс')
)
async def block_remove(event: SimpleUserEvent):
    user_id = await get_user_id(event)

    try:
        await event.api_ctx.account.unban(owner_id=user_id)
        await send_message_to_me(
            message=f'[💣] [id{user_id}|Пользователь] '
                    f'удален из черного списка.'
        )

    except APIError:
        await send_message_to_me(
            message=f'[💣] [id{user_id}|Пользователь] '
                    f'не находится в черном списке.'
        )


@simple_user_message_handler(
    social_router,
    MessageFromConversationTypeFilter(from_what='from_pm'),
    TextFilter('/чс'),
)
async def block_add_ls(event: SimpleUserEvent):
    await event.api_ctx.account.ban(owner_id=event.peer_id)
    await send_message_to_me(
        message=f'[💣] [id{event.peer_id}|Пользователь] '
                f'добавлен в черный список.',
    )
