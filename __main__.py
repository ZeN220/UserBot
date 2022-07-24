import asyncio
import logging

from src.commands.base import CommandManager
from src.config import Config
from src.database import connect_database
from src.dispatching import Dispatcher
from src.dispatching.middlewares import MIDDLEWARES
from src.dispatching.result_caster import ResultCaster, CASTERS
from src.sessions import Session, SessionManager, SessionsFile
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

    owner_session = await Session.create_from_tokens(
        user_token=config.vk.user_token,
        group_token=config.vk.bot_token,
        commands_prefix=config.vk.commands_prefix,
        dispatcher=dispatcher, modules=config.modules,
        delete_command_after=config.vk.delete_command_after
    )
    sessions_from_file = SessionsFile('sessions.toml')
    sessions = []
    for session in sessions_from_file.get_sessions():
        session = await Session.create_from_tokens(**session, dispatcher=dispatcher)
        sessions.append(session)

    CommandManager.setup_commands()
    await CommandManager.setup_commands_session(owner_session)
    for session in sessions:
        await CommandManager.setup_commands_session(session)

    SessionManager.add_session(owner_session, is_main=True)
    SessionManager.add_many_sessions(sessions)

    await SessionManager.run_all_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
