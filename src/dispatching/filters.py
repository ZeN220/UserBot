from typing import TYPE_CHECKING

from vkwave.bots.core.dispatching.filters.base import BaseFilter, FilterResult

from src.database import Template
if TYPE_CHECKING:
    from .event import UserEvent


class PrefixFilter(BaseFilter):
    async def check(self, event: 'UserEvent') -> FilterResult:
        prefix = event.session.commands_prefix
        text = event.object.object.text
        return FilterResult(text.startswith(prefix))


class TemplateFilter(BaseFilter):
    async def check(self, event: 'UserEvent') -> FilterResult:
        template = await Template.get_template(event.object.object.text, event.session.owner_id)
        if template:
            event['template'] = template
        return FilterResult(bool(template))
