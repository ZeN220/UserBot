import time

from vkwave.bots import (
    SimpleUserEvent,
    FromMeFilter,
    LevenshteinFilter
)

from utils import send_message_to_me
from dispatching import Router


messages_router = Router(
    'messages',
    'Команды для взаимодействиями с сообщениями.'
)


@messages_router.message_handler(
    LevenshteinFilter(['.чтение', '.msgread', '.read'], 2),
    FromMeFilter(True)
)
async def read_messages(event: SimpleUserEvent):
    await send_message_to_me(
        message='Начинаю прочтение всех сообщений...'
    )
    # Получение непрочитанных диалогов
    chats = (await event.api_ctx.messages.get_conversations(
        filter='unread', count=200
    )).response.items

    # Чтение диалогов + вычисление затраченного времени
    time1 = time.time()
    for chat in chats:
        chat = chat.conversation.peer.id
        await event.api_ctx.messages.mark_as_read(peer_id=chat)
    time2 = time.time()

    done_time = round(time2 - time1, 2)
    await send_message_to_me(
        message=f'Отлично! Было прочтено {len(chats)} '
                f'диалогов за {done_time} секунд',
    )
