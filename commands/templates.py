from vkwave.bots import (
    TextStartswithFilter,
    SimpleUserEvent,
    ReplyMessageFilter,
    MessageArgsFilter,
    TextFilter
)
import toml

from utils import send_message_to_me, TemplateFilter
from dispatching import Router


template_router = Router(
    'template',
    'Команды, для управления шаблонами'
)


@template_router.message_handler(
    TextStartswithFilter(('.addtemplate', '+шаблон')),
    MessageArgsFilter(1),
    ReplyMessageFilter()
)
async def add_template(event: SimpleUserEvent):
    templates = toml.load('templates.toml')

    name = event['args'][0]
    text = (await event.api_ctx.messages.get_by_id(
        message_ids=event.object.object.message_id
    )).response.items[0].reply_message.text

    templates.update(
        {name: text}
    )
    toml.dump(templates, open('templates.toml', 'w', encoding='utf-8'))

    await send_message_to_me('Шаблон успешно добавлен.')


@template_router.message_handler(
    TemplateFilter()
)
async def send_template(event: SimpleUserEvent):
    await event.api_ctx.messages.edit(
        message=event['answer'],
        message_id=event.object.object.message_id,
        peer_id=event.peer_id
    )


@template_router.message_handler(
    TextFilter(('.шаблоны', '.templates'))
)
async def get_templates(event: SimpleUserEvent):
    templates = toml.load('templates.toml')
    answer = [f'{name}: {text}\n' for name, text in templates.items()]
    answer = '\n'.join(answer)

    await send_message_to_me(
        f'Список существующих шаблонов:\n{answer}'
    )


@template_router.message_handler(
    TextStartswithFilter(('.removetemplate', '-шаблон')),
    MessageArgsFilter(1)
)
async def remove_template(event: SimpleUserEvent):
    templates = toml.load('templates.toml')
    name = event['args'][0]

    del templates[name]
    toml.dump(templates, open('templates.toml', 'w', encoding='utf-8'))

    await send_message_to_me(
        'Шаблон успешно удален.'
    )
