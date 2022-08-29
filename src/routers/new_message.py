from vkwave.bots import DefaultRouter, FromMeFilter
import re

from src.commands.base.manage import CommandManager
from src.commands.base.errors import NotEnoughArgs
from src.dispatching import UserEvent
from src.dispatching.filters import TemplateFilter, PrefixFilter, EventTypeFilter

# https://github.com/danyadev/longpoll-doc#%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D0%B5-4-%D0%BD%D0%BE%D0%B2%D0%BE%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B5
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
            await api_context.messages.delete(message_ids=message_id, delete_for_all=1)
            await api_context.messages.send(peer_id=peer_id, **template, random_id=0)
            return

    await api_context.messages.edit(
        message_id=message_id, peer_id=peer_id,
        keep_forward_messages=1, **template
    )


@new_message_router.registrar.with_decorator(PrefixFilter())
async def execute_command(event: UserEvent):
    event.object.object.text = event.object.object.text[1:].lstrip()
    command = CommandManager.find_command(
        session=event.session,
        text=event.object.object.text
    )
    if command is None:
        return

    session = event.session
    if session.delete_command_after:
        await event.api_ctx.messages.delete(
            delete_for_all=1, message_ids=event.object.object.message_id
        )

    # TODO: Обработка ошибка NotEnoughARgs в этом месте является не лучшим решением,
    #  ее стоит обрабатывать на более низком уровне
    try:
        response = await command.start(
            event, gateway=event['gateway'], api_context=event.api_ctx, session=event.session
        )
    except NotEnoughArgs:
        await event.session.send_service_message(
            f'[⌨] При написании команды «{event.object.object.text}» '
            f'было указано недостаточно аргументов.'
        )
    else:
        return response
