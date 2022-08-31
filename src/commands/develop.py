from typing import Optional, List
from enum import Enum
import json
import time

from vkwave.api import APIOptionsRequestContext

from src.dispatching import UserEvent
from src.services import HolderGateway
from .base import CommandResponse, BaseHandler, Module
from .filters import ParseUserFilter, ParseDataFromFwd, ParseDataFromReply, MainSessionFilter

develop_module = Module('develop')


@develop_module.register(
    name='get_peer_id', aliases=['peer', 'пир']
)
class GetPeerIDHandler(BaseHandler):
    async def execute(self, event: UserEvent) -> 'CommandResponse':
        return CommandResponse(
            response=f'[🔧] Peer ID данного чата: {event.object.object.peer_id}'
        )


@develop_module.register(
    ParseUserFilter(), name='get_user_id', aliases=['user', 'пользователь'],
    args_syntax=[r'(\d+)', '']
)
class GetUserIDHandler(BaseHandler):
    async def execute(
        self,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> 'CommandResponse':
        if users_ids is not None:
            # TODO: Костыль с конвертацией типов
            users_ids = map(str, users_ids)
            users_ids = '\n'.join(users_ids)
            return CommandResponse(
                response=f'[🧑] ID пользователей: \n{users_ids}'
            )
        return CommandResponse(
            response=f'[🧑] ID пользователя: {user_id}'
        )


@develop_module.register(
    ParseDataFromReply() | ParseDataFromFwd(), name='get_message_id',
    aliases=['message_id', 'ид_сообщения']
)
class GetMessageIDHandler(BaseHandler):
    async def execute(self, message_id: int, conversation_message_id: int) -> 'CommandResponse':
        return CommandResponse(
            response=f'[🔢] ID сообщения: {message_id}\n'
                     f'ID сообщения внутри диалога: {conversation_message_id}'
        )


@develop_module.register(
    name='get_message_json', aliases=['json', 'жсон']
)
class GetMessageJSONHandler(BaseHandler):
    async def execute(self, event: UserEvent) -> 'CommandResponse':
        extra_data = event.object.object.extra_message_data
        reply_message_id = json.loads(extra_data['reply'])['conversation_message_id']
        reply_message = await event.api_ctx.messages.get_by_conversation_message_id(
            conversation_message_ids=reply_message_id, peer_id=event.object.object.peer_id
        )
        model = reply_message.response.items[0].dict()

        try:
            result = self.validate_dict_to_json(model)
            return CommandResponse(response=result)
        except RecursionError:
            return CommandResponse(
                response='[⚠] Объект сообщения оказался слишком большим.'
            )

    def remove_enums_from_list(self, list_object: list) -> None:
        for index, element in enumerate(list_object):
            if isinstance(element, Enum):
                list_object[index] = {element.name: element.value}
            if isinstance(element, dict):
                self.remove_enums_from_dict(element)

    def remove_enums_from_dict(self, dict_object: dict) -> None:
        for key, value in dict_object.items():
            if isinstance(value, Enum):
                dict_object[key] = {value.name: value.value}
            if isinstance(value, dict):
                self.remove_enums_from_dict(value)
            if isinstance(value, list):
                self.remove_enums_from_list(value)
                dict_object[key] = value

    def validate_dict_to_json(self, dict_object: dict) -> str:
        self.remove_enums_from_dict(dict_object)
        response = json.dumps(dict_object, indent=4, ensure_ascii=False)
        return response


@develop_module.register(
    MainSessionFilter(), name='sql_eval', aliases=['sql', 'скл'],
    args_syntax='(?P<query>.+)'
)
class SQLEvalHandler(BaseHandler):
    async def execute(self, query: str, gateway: HolderGateway) -> 'CommandResponse':
        start_time = time.perf_counter()
        response = await gateway.run_raw_query(query)
        response = self.validate_list_to_json(response)
        end_time = time.perf_counter() - start_time
        return CommandResponse(
            response=f'[🗂] Результат выполнения запроса: \n\n{response}\n\n '
                     f'Затрачено времени: {end_time:.3f}s'
        )

    @staticmethod
    def validate_list_to_json(response: list) -> str:
        result = [list(element) for element in response]
        result = json.dumps(result, indent=4, ensure_ascii=False)
        return result


@develop_module.register(
    name='ping', aliases=['ping', 'пинг']
)
class PingHandler(BaseHandler):
    async def execute(self, api_context: APIOptionsRequestContext) -> 'CommandResponse':
        start_time = time.perf_counter()
        await api_context.users.get()
        end_time = time.perf_counter() - start_time
        return CommandResponse(
            response=f'[⏰] Задержка до VK API составляет: {end_time:.3f}s'
        )
