import asyncio
import contextlib
import io
import json
import time
from concurrent.futures import ProcessPoolExecutor
from enum import Enum
from typing import Optional, List, Tuple

from vkwave.api import APIOptionsRequestContext

from src.dispatching import UserEvent
from src.sessions import Session, SessionManager
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
    args_syntax=r'(\d+)?'
)
class GetUserIDHandler(BaseHandler):
    async def execute(
        self,
        user_id: Optional[int] = None,
        users_ids: Optional[List[int]] = None
    ) -> 'CommandResponse':
        if users_ids is not None:
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


@develop_module.register(
    MainSessionFilter(), name='eval', aliases=['eval', 'евал'],
    args_syntax=r'\n(?P<code>[\s\S]+)'
)
class EvalHandler(BaseHandler):
    async def execute(self, code: str) -> 'CommandResponse':
        """
        WARNING: Из-за создания ProcessPoolExecutor,
        данная команда может медленно работать на Windows OS
        Более подробное описание проблемы:
        https://stackoverflow.com/questions/64407653/slow-futures-processpoolexecutor-how-to-improve
        """
        result, end_time = await run_code(code)

        return CommandResponse(
            response=f'[💻] Выполнено! \n\n{result}\n\n Затрачено времени: {end_time:.3f}s'
        )


@develop_module.register(
    name='api_execute', aliases=['api', 'апи'],
    args_syntax=r'(?P<method>[\w\.]+) (?P<params>[\w\s=]+)?'
)
class APIExecuteHandler(BaseHandler):
    async def execute(self, session: Session, method: str, params: str) -> 'CommandResponse':
        params = parse_params_method(params)

        response = await session.user.api_context.api_request(method, params)
        result = json.dumps(response, indent=2, ensure_ascii=False)
        return CommandResponse(
            response=f'[🖨] Метод «{method}» выполнен! \n\n{result}'
        )


@develop_module.register(
    MainSessionFilter(), name='session_api_execute', aliases=['session_api', 'сессия_апи'],
    args_syntax=r'(?P<owner_id>\d+) (?P<method>[\w\.]+) (?P<params>[\w\s=]+)'
)
class SessionAPIExecuteHandler(BaseHandler):
    async def execute(self, owner_id: int, method: str, params: str) -> 'CommandResponse':
        session = SessionManager.get_session_by_owner_id(owner_id)
        params = parse_params_method(params)

        response = await session.user.api_context.api_request(method, params)
        result = json.dumps(response, indent=2, ensure_ascii=False)
        return CommandResponse(
            response=f'[🖨] Метод от имени [{owner_id}] «{method}» выполнен! \n\n{result}'
        )


def parse_params_method(params: str):
    params = params.split(' ')
    params = [param.split('=') for param in params]
    params = {key: value for key, value in params}
    return params


async def run_code(code: str) -> Tuple[str, float]:
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as pool:
        result, end_time = await loop.run_in_executor(pool, _run_code, code)
        return result, end_time


def _run_code(code: str) -> Tuple[str, float]:
    """
    Для упрощения работы с командой, любой код запускается через асинхронную функцию main
    """
    code_with_tabulation = "".join(
        f"\n {line}" for line in code.split("\n")
    )
    async_code = (
        f'import asyncio\n'
        f'async def main():\n'
        f'{code_with_tabulation}\n'
        f'asyncio.run(main())'
    )

    code_stdout = io.StringIO()
    with contextlib.redirect_stdout(code_stdout):
        start_time = time.perf_counter()
        exec(async_code)
        end_time = time.perf_counter() - start_time
    return code_stdout.getvalue(), end_time

