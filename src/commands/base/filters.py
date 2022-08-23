import re
from abc import ABC, abstractmethod
from typing import Optional, List, TYPE_CHECKING

from pydantic import BaseModel, Field
from vkwave.api import APIOptionsRequestContext

from src.dispatching import UserEvent
if TYPE_CHECKING:
    from .command import Command


class FilterResult(BaseModel):
    result: bool = Field(None, description='Result of checking filter')
    context: dict = Field(None, description='Values from filter')


class BaseFilter(ABC):
    @abstractmethod
    async def check(self, event: UserEvent, command: 'Command') -> FilterResult:
        ...


class ParseUserFilter(BaseFilter):
    USER_MENTION_REGEXP = re.compile(r'\[id(\d+)\|.+]')
    USER_URL_REGEXP = re.compile(r'vk\.com/(.+)')

    async def check(self, event: UserEvent, command: 'Command') -> FilterResult:
        user_context = event.session.user.api_context
        message_object = event.object.object
        from_text = await self.parse_from_text(message_object.text, user_context)
        if from_text is not None:
            return FilterResult(result=True, context={'user_id': from_text})

        marked_users = message_object.message_data.marked_users
        if marked_users:
            return FilterResult(result=True, context={'user_id': marked_users[0][1][0]})

        is_fwd = message_object.extra_message_data.get('fwd')
        if is_fwd is not None:
            users_ids = await self.parse_from_fwd(
                message_object.message_id, user_context
            )
            return FilterResult(result=True, context={'users_ids': users_ids})

        await event.session.send_service_message(
            f'[⚠] При попытке выполнить команду «{command.name}» '
            f'не удалось получить пользователя, на которого она будет действовать.'
        )
        return FilterResult(result=False)

    @staticmethod
    async def parse_from_fwd(
        message_id: int,
        api_context: APIOptionsRequestContext
    ) -> Optional[List[int]]:
        result = []
        response = (await api_context.messages.get_by_id(
            message_ids=message_id
        )).response.items[0]
        for fwd_message in response.fwd_messages:
            result.append(fwd_message.from_id)
        return result

    async def parse_from_url(self, url: str, api_context: APIOptionsRequestContext) -> Optional[int]:
        url_regexp = self.USER_URL_REGEXP.search(url)
        if not url_regexp:
            return
        result = await api_context.utils.resolve_screen_name(screen_name=url_regexp.group(1))
        if result.response.dict().get('object_id'):
            return result.response.object_id

    async def parse_from_text(self, text: str, api_context: APIOptionsRequestContext) -> Optional[int]:
        """
        Числовой ID из текста парсится только если он указан первым аргументом в команде.
        Например, эта команда сработает и спарсит 1:
        !бан 1
        Но из этой команды уже ничего не спарсится:
        !бан навечно 1
        """
        # TODO: Дикий костыль
        from_text = text.split()
        if len(from_text) > 1 and from_text[1].isdigit():
            return int(from_text[1])

        from_url = await self.parse_from_url(text, api_context)
        if from_url is not None:
            return from_url

        mention_regexp = self.USER_MENTION_REGEXP.search(text)
        if mention_regexp:
            return int(mention_regexp.group(1))
