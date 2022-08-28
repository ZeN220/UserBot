import json
import re
from typing import TYPE_CHECKING, Optional, List

from vkwave.api import APIOptionsRequestContext

from src.dispatching import UserEvent
from .base import BaseFilter, FilterResult

if TYPE_CHECKING:
    from src.commands.base.command import Command


class ParseUserFilter(BaseFilter):
    USER_MENTION_REGEXP = re.compile(r'\[id(\d+)\|.+]')
    USER_URL_REGEXP = re.compile(r'vk\.com/(.+)')

    async def check(self, event: UserEvent, command: 'Command') -> FilterResult:
        user_context = event.session.user.api_context
        message_object = event.object.object
        marked_users = message_object.message_data.marked_users
        if marked_users:
            return FilterResult(result=True, context={'user_id': marked_users[0][1][0]})

        from_text = await self.parse_from_text(message_object.text, user_context)
        if from_text is not None:
            return FilterResult(result=True, context={'user_id': from_text})

        extra = message_object.extra_message_data
        if extra.get('reply'):
            user_id = await self.parse_from_reply(message_object.message_id, user_context)
            return FilterResult(result=True, context={'user_id': user_id})

        if extra.get('fwd') is not None:
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
    async def parse_from_reply(
        message_id: int,
        api_context: APIOptionsRequestContext
    ) -> int:
        result = await api_context.messages.get_by_id(
            message_ids=message_id
        )
        return result.response.items[0].reply_message.from_id

    @staticmethod
    async def parse_from_fwd(
        message_id: int,
        api_context: APIOptionsRequestContext
    ) -> List[int]:
        result = []
        response = (await api_context.messages.get_by_id(
            message_ids=message_id
        )).response.items[0]
        for fwd_message in response.fwd_messages:
            result.append(fwd_message.from_id)
        return result

    async def parse_from_url(
        self, url: str, api_context: APIOptionsRequestContext
    ) -> Optional[int]:
        url_regexp = self.USER_URL_REGEXP.search(url)
        if not url_regexp:
            return
        result = await api_context.utils.resolve_screen_name(screen_name=url_regexp.group(1))
        if result.response.object_id is not None:
            return result.response.object_id

    async def parse_from_text(
        self, text: str, api_context: APIOptionsRequestContext
    ) -> Optional[int]:
        from_url = await self.parse_from_url(text, api_context)
        if from_url is not None:
            return from_url

        mention_regexp = self.USER_MENTION_REGEXP.search(text)
        if mention_regexp:
            return int(mention_regexp.group(1))

        from_text = text.split()
        if len(from_text) > 1:
            screen_name = from_text[1]
            if screen_name.isdigit():
                return int(screen_name)
            result = await api_context.utils.resolve_screen_name(screen_name=screen_name)
            return result.response.object_id


class ParseDataFromReply(BaseFilter):
    async def check(self, event: UserEvent, command: 'Command') -> FilterResult:
        reply = event.object.object.extra_message_data.get('reply')
        if not reply:
            return FilterResult(result=False)

        conversation_message_id = json.loads(reply)['conversation_message_id']
        message = (await event.api_ctx.messages.get_by_conversation_message_id(
            peer_id=event.object.object.peer_id, conversation_message_ids=conversation_message_id
        )).response.items[0]
        return FilterResult(
            result=True,
            context={'text': message.text, 'attachments': message.attachments}
        )


class ParseDataFromFwd(BaseFilter):
    async def check(self, event: UserEvent, command: 'Command') -> FilterResult:
        fwd = event.object.object.extra_message_data.get('fwd')
        if not fwd:
            return FilterResult(result=False)
        message = (await event.api_ctx.messages.get_by_id(
            message_ids=event.object.object.message_id
        )).response.items[0].fwd_messages[0]
        return FilterResult(
            result=True,
            context={'text': message.text, 'attachments': message.attachments}
        )
