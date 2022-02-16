from typing import List
import re

from vkwave.bots import (
    TextStartswithFilter,
    SimpleUserEvent,
    ReplyMessageFilter,
    MessageArgsFilter,
    TextFilter,
    PhotoUploader
)
import toml

from utils import send_message_to_me, config
from dispatching import Router, TemplateFilter


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
    uploader = PhotoUploader(event.api_ctx)

    name = event['args'][0]
    template = (await event.api_ctx.messages.get_by_id(
        message_ids=event.object.object.message_id
    )).response.items[0].reply_message

    attachments: List[str] = []

    for attachment in template.attachments:
        url = max(attachment.photo.sizes, key=lambda pic: pic.height).url
        attachment_id = await uploader.get_attachment_from_link(
            peer_id=config['VK']['user_id'],
            link=url
        )
        attachments.append(attachment_id)

    templates.update(
        {name: {'text': template.text, 'attachments': attachments}}
    )
    toml.dump(templates, open('templates.toml', 'w', encoding='utf-8'))

    await send_message_to_me('Шаблон успешно добавлен.')


@template_router.message_handler(
    TemplateFilter()
)
async def send_template(event: SimpleUserEvent):
    template = event["answer"]
    message_text = event.text[len(template['name']) + 1:]
    await event.api_ctx.messages.edit(
        message=template['text'] + message_text,
        message_id=event.object.object.message_id,
        peer_id=event.peer_id,
        attachment=template['attachments'],
        keep_forward_messages=1
    )


@template_router.message_handler(
    TextFilter(('.шаблоны', '.templates'))
)
async def get_templates(event: SimpleUserEvent):
    templates = toml.load('templates.toml')
    answer = []
    for template in templates.items():
        answer.append(f'{template[0]}: {template[1]["text"]}\n')
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
