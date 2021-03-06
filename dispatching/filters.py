from vkwave.bots.core.dispatching.filters.base import BaseFilter, FilterResult
from vkwave.bots import UserEvent
import toml


class TemplateFilter(BaseFilter):
    async def check(self, event: UserEvent) -> FilterResult:
        templates = toml.load('templates.toml')
        for template in templates.keys():
            text = event.object.object.text
            if text and text.split()[0] == f'.{template}':
                event['answer'] = {
                    'name': template,
                    'text': templates[template]['text'],
                    'attachments': templates[template]['attachments']
                }
                return FilterResult(True)
        return FilterResult(False)
