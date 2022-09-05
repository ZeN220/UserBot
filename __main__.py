import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.commands import templates_module, social_module, dialogs_module, develop_module, \
    chats_module, session_module
from src.commands.base.manager import ModulesManager
from src.config import Config
from src.dispatching import Dispatcher
from src.dispatching.middlewares import DatabaseMiddleware, EnvironmentMiddleware, \
    TextShieldingMiddleware, NoneObjectMiddleware
from src.dispatching.result_caster import ResultCaster, CASTERS
from src.routers import new_message_router
from src.sessions import Session, SessionManager
from src.sessions.from_database import load_sessions_from_database


async def main():
    config = Config.load_from_file('config.toml')
    logging.basicConfig(level=config.logging.level, format=config.logging.format)

    engine = create_async_engine(config.database.url, future=True)
    # Возможно, установка настройки expire_on_commit=False является не лучшим решением,
    # в будущем стоит использовать DTO
    session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    modules_manager = ModulesManager()
    modules_manager.add_module(develop_module)
    modules_manager.add_module(dialogs_module)
    modules_manager.add_module(social_module)
    modules_manager.add_module(templates_module)
    modules_manager.add_module(chats_module)
    modules_manager.add_module(session_module)
    modules_manager.sort_modules()

    caster = ResultCaster()
    dispatcher = Dispatcher(result_caster=caster)
    caster.casters = CASTERS
    dispatcher.add_router(new_message_router)
    dispatcher.add_middleware(NoneObjectMiddleware())
    dispatcher.add_middleware(DatabaseMiddleware(session_maker))
    dispatcher.add_middleware(EnvironmentMiddleware(
        modules_manager=modules_manager, dispatcher=dispatcher
    ))
    dispatcher.add_middleware(TextShieldingMiddleware())

    owner_session = await Session.create_from_tokens(
        user_token=config.vk.user_token,
        group_token=config.vk.group_token,
        commands_prefix=config.vk.commands_prefix,
        deactivate_modules=config.vk.deactivate_modules,
        delete_command_after=config.vk.delete_command_after
    )
    sessions = await load_sessions_from_database(database_session=session_maker())
    for session in sessions:
        SessionManager.add_session(session)
    SessionManager.add_session(owner_session, is_main=True)

    await SessionManager.run_all_polling(dispatcher)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
