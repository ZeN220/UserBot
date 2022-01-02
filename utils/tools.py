from typing import Optional, List
import re

from vkwave.bots import SimpleLongPollBot, DefaultRouter, SimpleUserEvent, SimpleLongPollUserBot
from vkwave.bots.core.dispatching.filters import BaseFilter
from vkwave.api import APIOptionsRequestContext
from tortoise import Tortoise
import toml


config = toml.load('config.toml')

bot = SimpleLongPollUserBot(tokens=config['VK']['user_token'])
if config['VK']['bot_token']:
    bot = SimpleLongPollBot(tokens=config['VK']['bot_token'],
                            group_id=config['VK']['group_id'])

USER_MENTION_REGEXP = re.compile(r"\[id(\d+)\|[^\]\[]+]")


class Router(DefaultRouter):
    def __init__(
        self,
        name: str,
        description: str,
        filters: Optional[List[BaseFilter]] = None
    ):
        super().__init__(filters)
        self.name = name
        self.description = description


async def set_my_id(api_ctx: APIOptionsRequestContext) -> None:
    result = await api_ctx.users.get()
    config['VK'].update({
        'user_id': result.response[0].id
    })
    toml.dump(config, open('config.toml', 'w', encoding='utf-8'))


async def database_init() -> None:
    await Tortoise.init(
        db_url='sqlite://logging.sqlite',
        modules={'models': ['database.message']}
    )
    await Tortoise.generate_schemas()


async def get_user_id(event: SimpleUserEvent) -> int:
    if event.object.object.message_data.marked_users:
        return event.object.object.message_data.marked_users[0][1][0]
    if event.object.object.extra_message_data.get('fwd'):
        user_id = (
            await event.api_ctx.messages.get_by_id(message_ids=event.object.object.message_id)
        ).response.items[0].fwd_messages[0].from_id
        return user_id

    user_obj = event.text.split()[1]

    if user_obj.isdigit():
        return int(user_obj)

    user_id = USER_MENTION_REGEXP.findall(user_obj)
    if user_id:
        return int(user_id[0])

    domain = user_obj.split('/')[-1]
    if domain.startswith('id'):
        return int(domain[2:])

    user_id = (await event.api_ctx.utils.resolve_screen_name(screen_name=domain)).response.object_id
    return user_id
