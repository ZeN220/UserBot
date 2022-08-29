import json
import logging
from typing import TYPE_CHECKING

from vkwave.api import APIOptionsRequestContext

from src.sessions.manage import SessionManager
if TYPE_CHECKING:
    from src.sessions.session import Session

logger = logging.getLogger(__name__)


async def cant_add_user_chat(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 15 ошибки от VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)
    await session.send_service_message(
        '[⚠] Не удалось добавить пользователя в чат. Возможно, он запретил приглашать себя в чаты.'
    )


async def you_arent_admin_chat(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 925 ошибки от VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)
    await session.send_service_message(
        '[⚠] Вы не являетесь администратором в данном чате.'
    )


async def add_undefined_user_friend(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 177 ошибки от VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)
    await session.send_service_message(
        '[⚠] Пользователь не найден и не будет добавлен в список друзей.'
    )


async def add_user_in_your_blacklist_friend(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 176 ошибки от VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)
    await session.send_service_message(
        '[⚠] Вы не можете добавить данного пользователя список друзей,'
        'потому что он находится в вашем черном списке.'
    )


async def add_himself_friend(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 174 ошибки от VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)
    await session.send_service_message(
        '[⚠] Вы не можете добавить самого себя в список друзей.'
    )


async def add_user_in_him_blacklist_friend(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 175 ошибки от VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)
    await session.send_service_message(
        '[⚠] Вы не можете добавить данного пользователя в список друзей, '
        'потому что находитесь у него в черном списке.'
    )


async def too_many_requests(error: dict, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 6 ошибки от VK API
    """
    if error.get('execute_errors'):
        return await api_ctx.api_request(
            'execute', params={'code': error['request_params']['code']}
        )
    method = error["error"]["request_params"][0]["value"]
    """
    При вызове messages.send и возникновении ошибки, 
    VK API не возвращает текст сообщения, из-за этого повторить запрос нельзя. 
    (На самом деле можно, но для этого нужно писать достаточно сложную реализацию)
    """
    if method == 'messages.send':
        return

    request_params = {}
    for param in error["error"]["request_params"][2:]:
        if param["key"] == "v":
            continue
        request_params[param["key"]] = param["value"]

    return await api_ctx.api_request(method, params=request_params)


async def user_auth_failed(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 5 ошибки от VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)

    await session.send_service_message(
        '[🚪] При авторизации с вашего аккаунта произошла ошибка. '
        'Ваша сессия будет автоматически удалена.'
    )
    SessionManager.delete_session(session)


async def default_error_handler(error: dict, api_ctx: APIOptionsRequestContext):
    """
    Хендлер для незарегистрированных ошибок VK API
    """
    session = await _get_session_from_api_ctx(api_ctx)

    is_execute_error = error.get('execute_errors')
    if not is_execute_error:
        errors = [error['error']]
    else:
        errors = is_execute_error

    for error_ in errors:
        if is_execute_error:
            method = error_['method']
        else:
            method = error_['request_params'][0]['value']
        description = error_['error_msg']

        await session.send_service_message(
            f'[⚠] При выполнении метода «{method}» произошла ошибка:'
            f'\n[{error_["error_code"]}] {description}'
        )

    error_dump = json.dumps(error, indent=2)
    logger.error(f'От имени сессии [{session.owner_id}] произошла ошибка:\n{error_dump}')


async def cant_send_message_handler(error: dict, api_ctx: APIOptionsRequestContext):
    owner_id = list(filter(
        lambda param: param['key'] == 'peer_id',
        error['error']['request_params']
    ))[0]['value']
    group = await api_ctx.groups.get_by_id()
    main_session = SessionManager.main_session

    await main_session.send_service_message(
        f'[📩] [id{owner_id}|Пользователь] запретил отправлять '
        f'[club{group.response[0].id}|группе] сообщения.'
    )


ERROR_HANDLERS = {
    5: user_auth_failed,
    6: too_many_requests,
    15: cant_add_user_chat,
    174: add_himself_friend,
    175: add_user_in_him_blacklist_friend,
    176: add_user_in_your_blacklist_friend,
    177: add_undefined_user_friend,
    925: you_arent_admin_chat,
}
GROUP_ERROR_HANDLERS = {901: cant_send_message_handler}


async def _get_session_from_api_ctx(api_ctx: APIOptionsRequestContext) -> 'Session':
    token = await api_ctx.api_options.get_token()
    session = SessionManager.get_session_from_token(token)
    return session
