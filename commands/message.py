import time

from vkwave.bots import (
    simple_user_message_handler,
    SimpleUserEvent,
    FromMeFilter,
    LevenshteinFilter
)

from utils import bot, config
from dispatching import Router


my_id = config['VK']['user_id']
messages_router = Router(
    'messages',
    'Команды для взаимодействиями с сообщениями.'
)


@messages_router.message_handler(
    LevenshteinFilter(['.чтение', '.msgread', '.read'], 2),
    FromMeFilter(True)
)
async def read_messages(event: SimpleUserEvent):
    send_msg_id = (await bot.api_context.messages.send(
        peer_id=my_id,
        message='Начинаю прочтение всех сообщений...',
        random_id=0
    )).response
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
    await bot.api_context.messages.edit(
        message=f'Отлично! Было прочтено {len(chats)} '
                f'диалогов за {done_time} секунд',
        message_id=send_msg_id,
        peer_id=my_id
    )
