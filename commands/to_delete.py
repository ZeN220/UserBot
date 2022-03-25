import asyncio
from time import time
from typing import List
import re

from vkwave.api import APIOptionsRequestContext
from vkwave.api.methods._error import APIError
from vkwave.bots import (
    SimpleUserEvent,
    FromMeFilter,
    TextStartswithFilter
)

from dispatching import Router
from utils import config


to_delete_list: List[int] = []
to_delete_router = Router(
    'to_delete',
    'Команда для удаления указанного количество сообщений.'
)


async def get_messages(
    count: int,
    api_ctx: APIOptionsRequestContext,
    peer_id: int
) -> List[int]:
    message_ids = []
    history = (await api_ctx.messages.get_history(peer_id=peer_id, count=50 + count)).response.items

    for message in history:
        if len(message_ids) > count:
            break
        if message.from_id == config['VK']['user_id']:
            message_ids.append(message.id)

    return message_ids


async def edit_messages(message_ids: List[int], event: SimpleUserEvent) -> None:
    not_edtied_messages = message_ids.copy()
    for message in message_ids:
        try:
            start_time = time()
            await event.api_ctx.messages.edit(
                peer_id=event.peer_id, message='&#13;', message_id=message
            )
            not_edtied_messages.pop()

        except APIError as error:
            if error.code == 6:
                await asyncio.sleep(0.3)
                await edit_messages(not_edtied_messages, event)


@to_delete_router.message_handler(
    TextStartswithFilter(config['to_delete_trigger']),
    FromMeFilter(True)
)
async def to_delete(event: SimpleUserEvent):
    peer_id = event.object.object.peer_id
    text = event.object.object.text
    get_digit = re.findall(r'(\d+)', text)
    # Найдено ли число в сообщение, если нет, то указывается 1
    to_delete_count = 1 if not get_digit else int(get_digit[0])

    is_editing = (len(text) > 3) and (text[2] == config['to_delete_argument'])

    messages = await get_messages(to_delete_count, event.api_ctx, peer_id)
    if is_editing:
        await edit_messages(messages, event)

    await event.api_ctx.messages.delete(
        message_ids=messages,
        delete_for_all=1
    )

    to_delete_list.clear()
