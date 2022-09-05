from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from .session import SessionGateway
from .template import TemplateGateway
from .deactivate_module import DeactivateModuleGateway


@dataclass
class HolderGateway:
    database_session: AsyncSession
    template: TemplateGateway = field(init=False)
    session: SessionGateway = field(init=False)
    deactivate_module: DeactivateModuleGateway = field(init=False)

    def __post_init__(self):
        self.template = TemplateGateway(self.database_session)
        self.session = SessionGateway(self.database_session)
        self.deactivate_module = DeactivateModuleGateway(self.database_session)
