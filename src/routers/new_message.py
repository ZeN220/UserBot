from vkwave.bots import DefaultRouter, FromMeFilter

from src.commands.base import CommandManager
from src.dispatching import UserEvent
from src.dispatching.filters import TemplateFilter, PrefixFilter, EventTypeFilter
from src.commands.base.errors import NotEnoughArgs

# https://github.com/danyadev/longpoll-doc#%D1%81%D0%BE%D0%B1%D1%8B%D1%82%D0%B8%D0%B5-4-%D0%BD%D0%BE%D0%B2%D0%BE%D0%B5-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D0%B5
new_message_router = DefaultRouter(
    [EventTypeFilter(4), FromMeFilter(True)]
)


@new_message_router.registrar.with_decorator(TemplateFilter())
async def send_template(event: UserEvent):
    template = event['template']
    await event.session.user.api_context.messages.edit(
        message_id=event.object.object.message_id, peer_id=event.object.object.peer_id,
        keep_forward_messages=1, **template
    )


@new_message_router.registrar.with_decorator(PrefixFilter())
async def execute_command(event: UserEvent):
    command = await CommandManager.find_command(event)
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
        response = await command.start(event, event['gateway'])
    except NotEnoughArgs:
        await event.session.send_service_message(
            f'[⌨] При написании команды «{event.object.object.text}» '
            f'было указано недостаточно аргументов.'
        )
    else:
        return response
