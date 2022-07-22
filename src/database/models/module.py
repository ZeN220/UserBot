from typing import TYPE_CHECKING, Optional, List

from tortoise import fields, Model

from .session_model import SessionModel
if TYPE_CHECKING:
    from src.sessions import Session


class Module(Model):
    session: 'SessionModel' = fields.ForeignKeyField('models.SessionModel')
    name = fields.CharField(max_length=32)
    is_activate = fields.BooleanField()

    @classmethod
    async def get_activate_modules(cls, session: 'Session') -> List[str]:
        result = []
        session = await SessionModel.get_model_from_session(session)
        response = await cls.filter(session=session)
        for module in response:
            if module.is_activate:
                result.append(module.name)
        return result

    @classmethod
    async def is_activate_module(cls, session: 'Session', module: str) -> Optional[bool]:
        session = await SessionModel.get_model_from_session(session)
        module = await cls.get(session=session, module=module)
        return module.is_activate

    class Meta:
        table = 'modules'
