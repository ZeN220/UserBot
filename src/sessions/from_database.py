from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from src.services import SessionGateway
from src.sessions import Session, InvalidSessionError


async def get_sessions_from_database(database_session: AsyncSession) -> List[dict]:
    gateway = SessionGateway(database_session)
    sessions = await gateway.get_all_with_deactivate_modules()
    sessions_as_dict = []
    for session in sessions:
        sessions_as_dict.append({
            'user_token': session.user_token,
            'group_token': session.group_token,
            'commands_prefix': session.commands_prefix,
            'delete_command_after': session.delete_command_after,
            'deactivate_modules': [
                deactivate_module.module for deactivate_module in session.deactivate_modules
            ]
        })
    return sessions_as_dict


async def load_sessions_from_database(
    database_session: AsyncSession
) -> List[Session]:
    result = []
    gateway = SessionGateway(database_session)
    sessions = await get_sessions_from_database(database_session)
    for session in sessions:
        try:
            session = await Session.create_from_tokens(**session)
        except InvalidSessionError:
            await gateway.delete_by_user_token(user_token=session['user_token'])
        else:
            result.append(session)
    return result
