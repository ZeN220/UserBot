import json
import logging

from vkwave.api import APIOptionsRequestContext

from src.sessions.manage import SessionManager

logger = logging.getLogger(__name__)


async def user_auth_failed(_, api_ctx: APIOptionsRequestContext):
    """
    Хендлер 5 ошибкой от VK API
    """
    token = await api_ctx.api_options.get_token()
    session = SessionManager.get_session_from_token(token)

    await session.send_service_message(
        f'[🚪] При авторизации вашего аккаунта произошла ошибка. Ваша сессия будет автоматически удалена.'
    )
    SessionManager.delete_session(session)


async def default_error_handler(error: dict, api_ctx: APIOptionsRequestContext):
    """
    Хендлер для незарегистрированных ошибок VK API
    """
    token = await api_ctx.api_options.get_token()
    session = SessionManager.get_session_from_token(token)

    method = error['error']['request_params'][0]['value']
    description = error['error']['error_msg']
    await session.send_service_message(
        f'[⚠] При выполнении метода {method} произошла ошибка:\n{description}'
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
        f'[📩] [id{owner_id}|Пользователь] запретил отправлять [club{group.response[0].id}|группе] сообщения.'
    )


ERROR_HANDLERS = {
    5: user_auth_failed
}
GROUP_ERROR_HANDLERS = {901: cant_send_message_handler}
