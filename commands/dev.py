from time import time

from vkwave.bots import (
    simple_user_message_handler,
    SimpleUserEvent,
    FromMeFilter,
    MessageFromConversationTypeFilter,
    TextStartswithFilter,
    TextFilter
)

from utils import config, bot, Router, get_user_id


my_id = config['VK']['user_id']
dev_router = Router(
    'system',
    'Команды для разработчиков ботов.'
)
dev_router.registrar.add_default_filter(FromMeFilter(True))


@simple_user_message_handler(
    dev_router,
    MessageFromConversationTypeFilter(from_what='from_chat'),
    TextFilter(('.peerid', '.пирид'))
)
async def peer_id(event: SimpleUserEvent):
    await bot.api_context.messages.send(
        message=f'Peer_id -- {event.object.object.peer_id}',
        peer_id=my_id,
        random_id=0
    )


@simple_user_message_handler(
    dev_router,
    TextStartswithFilter(('.id', '.ид'))
)
async def user_id_from_msg(event: SimpleUserEvent):
    user_id = await get_user_id(event)
    await bot.api_context.messages.send(
        message=f'UserID -- {user_id}',
        peer_id=my_id,
        random_id=0
    )


@simple_user_message_handler(
    dev_router,
    TextFilter('.msgid')
)
async def get_message_id(event: SimpleUserEvent):
    reply = event.object.object.extra_message_data.get('reply')
    fwd = event.object.object.extra_message_data.get('fwd')
    message_id = (await event.api_ctx.messages.get_by_id(
        message_ids=event.object.object.message_id
    )).response.items[0]

    if reply:
        message_id = message_id.reply_message.id
    elif fwd:
        message_id = message_id.fwd_messages[0].id

    await bot.api_context.messages.send(
        message=f'MessageID -- {message_id}',
        peer_id=my_id,
        random_id=0
    )


@simple_user_message_handler(
    dev_router,
    TextStartswithFilter(('.eval', '.евал'))
)
async def run_eval(event: SimpleUserEvent):
    """
    Выполнение указанного кода
    """
    code = event.object.object.text[5:]
    result_eval = eval(code)
    await bot.api_context.messages.send(
        message=result_eval,
        peer_id=my_id,
        random_id=0
    )


@simple_user_message_handler(
    dev_router,
    TextFilter(('.ping', '.пинг'))
)
async def ping(event: SimpleUserEvent):
    msg_id = event.object.object.message_id
    before_time = time()
    await event.api_ctx.messages.delete(
        message_ids=msg_id,
        delete_for_all=1
    )
    after_time = time()
    ping_time = round(after_time - before_time, 3)
    await bot.api_context.messages.send(
        message=f'Задержка составляет {ping_time} секунд',
        peer_id=my_id,
        random_id=0
    )
