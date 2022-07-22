import asyncio
import logging

from src.commands.base import CommandManager
from src.config import Config
from src.database import SessionModel, connect_database
from src.dispatching import Dispatcher
from src.dispatching.middlewares import MIDDLEWARES
from src.dispatching.result_caster import ResultCaster, CASTERS
from src.sessions import Session, SessionManager
from src.routers import setup_router


async def main():
    config = Config.load_from_file('config.toml')
    logging.basicConfig(level=config.logging.level, format=config.logging.format)

    caster = ResultCaster()
    dispatcher = Dispatcher(result_caster=caster)
    caster.casters = CASTERS
    dispatcher.middleware_manager.middlewares = MIDDLEWARES
    setup_router(dispatcher)

    await connect_database(config.database.url)

    # TODO: Переписать говнокод для получениях активных модулей из сессии
    activate_modules = list(filter(lambda module: getattr(config.modules, module),  config.modules.keys()))
    # Получаем список возможных модулей из полей конфига
    CommandManager.modules = list(config.modules.keys())

    owner_session = await Session.create_from_tokens(
        user_token=config.vk.user_token,
        bot_token=config.vk.bot_token,
        commands_prefix=config.vk.commands_prefix,
        dispatcher=dispatcher,
        delete_command_after=config.vk.delete_command_after
    )
    sessions_from_database = await SessionModel.create_all_sessions(dispatcher=dispatcher)

    CommandManager.setup_commands()
    await CommandManager.setup_commands_session(owner_session, modules=activate_modules)
    for session in sessions_from_database:
        await CommandManager.setup_commands_session(session)

    SessionManager.add_session(owner_session, is_main=True)
    SessionManager.add_many_sessions(sessions_from_database)

    await SessionManager.run_all_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
