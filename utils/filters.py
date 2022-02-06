from vkwave.bots.core.dispatching.filters.base import BaseFilter, FilterResult
from vkwave.bots import UserEvent
import toml


class TemplateFilter(BaseFilter):
    async def check(self, event: UserEvent) -> FilterResult:
        templates = toml.load('templates.toml')
        for template in templates.keys():
            if f'.{template}' == event.object.object.text:
                event['answer'] = templates[template]
                return FilterResult(True)
        return FilterResult(False)
