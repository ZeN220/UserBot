import re
import asyncio

from vkwave.bots import DefaultRouter, FromMeFilter

from src.commands.base.manager import ModulesManager
from src.dispatching import UserEvent
from src.dispatching.filters import TemplateFilter, PrefixFilter, EventTypeFilter, ToDeleteFilter

new_message_router = DefaultRouter(
    [EventTypeFilter(4), FromMeFilter(True)]
)
AUDIO_DOCUMENT_REGEXP = re.compile(r'doc\d+_\d+_\w+')

"""
Динамические команды, такие как вызов шаблонов и удаление сообщений должны 
выноситься в отдельный роутер
"""


@new_message_router.registrar.with_decorator(ToDeleteFilter())
async def to_delete(event: UserEvent):
    # + 1 Нужен для удаления сообщения, которое вызвало команду
    count = event['count'] + 1
    peer_id = event.object.object.peer_id

    message_ids = []
    history = await event.api_ctx.messages.get_history(
        peer_id=peer_id, count=50+count
    )
    for message in history.response.items:
        if len(message_ids) >= count:
            break

        if message.from_id == event.session.owner_id and not message.action:
            message_id = message.id
            message_ids.append(message_id)
            await event.api_ctx.messages.edit(
                message_id=message_id,
                peer_id=peer_id,
                message='&#13;'
            )
    await event.api_ctx.messages.delete(message_ids=message_ids, delete_for_all=1)


@new_message_router.registrar.with_decorator(TemplateFilter())
async def send_template(event: UserEvent):
    api_context = event.session.user.api_context
    message_id = event.object.object.message_id
    peer_id = event.object.object.peer_id
    template = event['template']

    if template['attachment']:
        is_audio = AUDIO_DOCUMENT_REGEXP.match(template['attachment'][0])
        if is_audio:
            await asyncio.gather(
                api_context.messages.delete(message_ids=message_id, delete_for_all=1),
                api_context.messages.send(peer_id=peer_id, **template, random_id=0)
            )
            return

    await api_context.messages.edit(
        message_id=message_id, peer_id=peer_id,
        keep_forward_messages=1, **template
    )


@new_message_router.registrar.with_decorator(PrefixFilter())
async def execute_command(event: UserEvent):
    manager: ModulesManager = event['modules_manager']
    text = event.object.object.text[1:].lstrip()
    command = manager.find_command(
        session=event.session,
        text=text
    )
    if command is None:
        return

    session = event.session
    if session.delete_command_after:
        await event.api_ctx.messages.delete(
            delete_for_all=1, message_ids=event.object.object.message_id
        )

    response = await command.start(
        event, gateway=event['gateway'], api_context=event.api_ctx, session=event.session,
        dispatcher=event['dispatcher'], modules_manager=manager
    )
    return response
