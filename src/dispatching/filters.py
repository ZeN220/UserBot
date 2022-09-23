from vkwave.bots.core.dispatching.filters.base import BaseFilter, FilterResult

from .event import UserEvent


class EventTypeFilter(BaseFilter):
    def __init__(self, *events_ids: int):
        self.events_ids = events_ids

    async def check(self, event: 'UserEvent') -> FilterResult:
        if event.object is None:
            return FilterResult(False)
        return FilterResult(event.object.object.event_id in self.events_ids)


class PrefixFilter(BaseFilter):
    async def check(self, event: 'UserEvent') -> FilterResult:
        prefix = event.session.commands_prefix
        text = event.object.object.text
        return FilterResult(text.startswith(prefix))


class TemplateFilter(BaseFilter):
    async def check(self, event: 'UserEvent') -> FilterResult:
        text = event.object.object.text
        if len(text) > 64 or 'templates' in event.session.deactivate_modules:
            return FilterResult(False)

        gateway = event['gateway']
        template = await gateway.template.get(text, event.session.owner_id)
        if template:
            attachments = [attachment.document for attachment in template.attachments]
            event['template'] = {'message': template.answer, 'attachment': attachments}
        return FilterResult(bool(template))


class ToDeleteFilter(BaseFilter):
    async def check(self, event: 'UserEvent') -> FilterResult:
        session = event.session
        text = event.object.object.text

        to_delete = session.settings.get('to_delete')
        argument = to_delete.get('argument')
        valid_strings = [trigger + argument for trigger in to_delete.get('triggers')]
        if text.startswith(tuple(valid_strings)):
            count = text.split(argument)
            if len(count) == 1:
                event['count'] = 1
                return FilterResult(True)

            count = count[1]
            if not count.isdigit():
                return FilterResult(False)
            else:
                event['count'] = int(count)
                return FilterResult(True)
        return FilterResult(False)
