from typing import TYPE_CHECKING

from vkwave.bots import DefaultRouter

from src.commands.base import CommandManager
from src.dispatching.filters import TemplateFilter, PrefixFilter
from src.dispatching import UserEvent
if TYPE_CHECKING:
    from src.dispatching import Dispatcher


new_message_router = DefaultRouter()


@new_message_router.registrar.with_decorator(TemplateFilter())
async def send_template(event: UserEvent):
    template = event['template']
    await event.session.user.api_context.messages.edit(
        message_id=event.object.object.message_id, peer_id=event.object.object.peer_id,
        keep_forward_messages=1, **template
    )


@new_message_router.registrar.with_decorator(PrefixFilter())
async def send_command(event: UserEvent):
    command, context = await CommandManager.find_command(event)
    if not command:
        return

    session = event.session
    if session.delete_command_after:
        await event.api_ctx.messages.delete(
            delete_for_all=1, message_ids=event.object.object.message_id
        )

    response = await command.start(**context)
    return response


def setup_router(dispatcher: 'Dispatcher'):
    dispatcher.add_router(new_message_router)
