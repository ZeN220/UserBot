import re
import asyncio

from vkwave.bots import DefaultRouter, FromMeFilter

from src.commands.base.manager import ModulesManager
from src.dispatching import UserEvent
from src.dispatching.filters import TemplateFilter, PrefixFilter, EventTypeFilter

new_message_router = DefaultRouter(
    [EventTypeFilter(4), FromMeFilter(True)]
)
AUDIO_DOCUMENT_REGEXP = re.compile(r'doc\d+_\d+_\w+')


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
