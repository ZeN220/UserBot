from typing import List
import re

from vkwave.bots import (
    SimpleUserEvent,
    FromMeFilter,
    TextStartswithFilter
)

from dispatching import Router
from utils import config


to_delete_list: List[int] = []
to_delete_router = Router(
    __name__,
    'Команда для удаления указанного количество сообщений.'
)


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

    messages = (await event.api_ctx.messages.get_history(
        peer_id=peer_id,
        count=50 + to_delete_count
    )).response.items
    for message in messages:
        if message.from_id == config['VK']['user_id'] and len(to_delete_list) <= to_delete_count:
            to_delete_list.append(message.id)
            if is_editing:
                await event.api_ctx.messages.edit(
                    peer_id=peer_id,
                    message='&#13;',
                    message_id=message.id
                )

    await event.api_ctx.messages.delete(
        message_ids=to_delete_list,
        delete_for_all=1
    )

    to_delete_list.clear()
