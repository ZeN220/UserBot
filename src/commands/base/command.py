from typing import List, TYPE_CHECKING, Type, Union, Optional, Tuple
import re

if TYPE_CHECKING:
    from src.dispatching import UserEvent
    from .filters import BaseFilter
    from .types import CommandResponse
    from .handler import BaseHandler


class Command:
    def __init__(
        self,
        name: str,
        module: str,
        aliases: List[str],
        handler: Type['BaseHandler'],
        priority: int,
        pattern: Union[str, re.Pattern],
        filters: Optional[List['BaseFilter']] = None,
    ):
        self.name = name
        self.module = module
        self.aliases = aliases
        self.handler = handler
        self.priority = priority
        self.filters = filters if filters else []
        self.pattern = re.compile(pattern) if isinstance(pattern, str) else pattern

    async def check_filters(self, event: 'UserEvent') -> Tuple[bool, dict]:
        context = {}
        for filter_ in self.filters:
            response = await filter_.check(event)
            if response.result:
                context.update(response.context)
                continue
            return False, {}
        return True, context

    def check_aliases(self, text: str) -> bool:
        for alias in self.aliases:
            if text == alias:
                return True

    async def is_suitable(self, event: 'UserEvent') -> Optional[dict]:
        text = event.object.object.text
        is_command = self.check_aliases(text)
        if not is_command:
            return

        result, context = await self.check_filters(event)
        if result:
            return context
        return

    async def start(self, **kwargs) -> 'CommandResponse':
        handler = self.handler()
        return await handler.run(**kwargs)
