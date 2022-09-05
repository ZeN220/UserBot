from typing import Optional

from src.dispatching import Dispatcher
from src.services import HolderGateway
from src.sessions import SessionManager, Session, InvalidSessionError
from .base import Module, CommandResponse, BaseHandler
from .filters import MainSessionFilter
from .base.manager import ModulesManager

session_module = Module('session')


@session_module.register(
    MainSessionFilter(), name='add_session', aliases=['addsession', 'session+', 'сессия+'],
    args_syntax=(
        r'(?P<access_token>.+) (?P<commands_prefix>.{1,8}) '
        r'(?P<delete_command_after>true|false)\s?(?P<group_token>.+)?'
    )
)
class AddSessionHandler(BaseHandler):
    async def execute(
        self,
        dispatcher: Dispatcher,
        gateway: HolderGateway,
        access_token: str,
        commands_prefix: str,
        delete_command_after: bool,
        group_token: Optional[str] = None,
    ) -> CommandResponse:
        main_session = SessionManager.main_session
        group_token = group_token or main_session.group.group_token
        session_data = {
            'user_token': access_token, 'group_token': group_token,
            'commands_prefix': commands_prefix, 'delete_command_after': delete_command_after,
        }

        try:
            session = await Session.create_from_tokens(**session_data)
        except InvalidSessionError:
            return CommandResponse(response='[🔐] Вы указали неверный токен сессии.')

        session_data.update({'group_id': session.group.group_id})
        SessionManager.add_session(session)
        await gateway.session.create(**session_data, owner_id=session.owner_id)
        await session.run_polling(dispatcher)

        return CommandResponse(
            response='[🔓] Авторизация от имени данной сессии прошла успешно.'
        )


@session_module.register(
    MainSessionFilter(), name='delete_session',
    aliases=['deletesession', 'removesession', 'session-', 'сессия-'],
    args_syntax=r'(?P<owner_id>\d+)'
)
class DeleteSessionHandler(BaseHandler):
    async def execute(self, owner_id: int, gateway: HolderGateway) -> 'CommandResponse':
        session = SessionManager.delete_session_by_owner_id(owner_id)
        await session.close_session()
        await gateway.session.delete_by_owner_id(owner_id)
        return CommandResponse(
            response='[🚪] Сессия успешно удалена.'
        )


@session_module.register(
    MainSessionFilter(), name='get_sessions', aliases=['sessions', 'сессии'],
    args_syntax=r'(?P<group_id>\d+)?'
)
class GetSessions(BaseHandler):
    async def execute(
        self, gateway: HolderGateway, group_id: Optional[int] = None
    ) -> 'CommandResponse':
        if group_id is not None:
            sessions = await gateway.session.get_by_group_id(group_id)
        else:
            sessions = await gateway.session.get_all()

        response = []
        for index, session in enumerate(sessions):
            owner_id = session.owner_id
            group_id = session.group_id
            response.append(
                f'{index + 1}. [[id{owner_id}|{owner_id}]] '
                f'Привязан к группе [[club{group_id}|club{group_id}]]'
            )
        response = '\n'.join(response)
        return CommandResponse(
            response=f'[💼] Список активных сессий: \n{response}'
        )


@session_module.register(
    name='session_info', aliases=['session', 'сессия']
)
class GetSessionInfoHandler(BaseHandler):
    async def execute(
        self, session: Session, modules_manager: ModulesManager
    ) -> 'CommandResponse':
        deactivate_modules = session.deactivate_modules
        all_modules_name = modules_manager.get_modules_names()
        activate_modules = set(all_modules_name) - set(deactivate_modules)
        response = []
        count_modules = 1
        for module in activate_modules:
            response.append(
                f'{count_modules}. [✅] {module}'
            )
            count_modules += 1
        for module in deactivate_modules:
            response.append(
                f'{count_modules}. [❌] {module}'
            )
            count_modules += 1
        response = '\n'.join(response)
        return CommandResponse(
            response=f'Список ваших модулей: \n{response}'
        )


@session_module.register(
    ~MainSessionFilter(), name='activate_module', aliases=['модуль+', 'module+'],
    args_syntax=r'(?P<module_name>\w+)'
)
class ActivateModuleHandler(BaseHandler):
    async def execute(
        self,
        gateway: HolderGateway,
        session: Session,
        module_name: str,
        modules_manager: ModulesManager
    ) -> 'CommandResponse':
        deactivate_modules = session.deactivate_modules
        all_modules = modules_manager.get_modules_names()
        if module_name not in all_modules or module_name not in deactivate_modules:
            return CommandResponse(
                response=f'[⚠] Модуля с названием «{module_name}» '
                         f'не существует или он у вас уже активирован.'
            )
        deactivate_modules.remove(module_name)
        await gateway.deactivate_module.delete_by_owner_id_and_name(module_name, session.owner_id)
        return CommandResponse(
            response=f'[📗] Модуль «{module_name}» успешно активирован.'
        )


@session_module.register(
    ~MainSessionFilter(), name='deactivate_module', aliases=['module-', 'модуль-'],
    args_syntax=r'(?P<module_name>\w+)'
)
class DeactivateModuleHandler(BaseHandler):
    async def execute(
        self,
        gateway: HolderGateway,
        session: Session,
        module_name: str,
        modules_manager: ModulesManager
    ) -> 'CommandResponse':
        deactivate_modules = session.deactivate_modules
        all_modules = modules_manager.get_modules_names()
        if module_name not in all_modules or module_name in deactivate_modules:
            return CommandResponse(
                response=f'[⚠] Модуля с названием «{module_name}» '
                         f'не существует или он у вас уже деактивирован.'
            )
        deactivate_modules.append(module_name)
        await gateway.deactivate_module.create(module_name, session.owner_id)
        return CommandResponse(
            response=f'[📙] Модуль «{module_name}» успешно деактивирован.'
        )
