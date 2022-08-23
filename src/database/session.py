from sqlalchemy import Column, Integer, Text, String, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class SessionModel(Base):
    __tablename__ = 'sessions'

    owner_id = Column(Integer, primary_key=True, unique=True, index=True)
    user_token = Column(Text)
    group_token = Column(Text)
    commands_prefix = Column(String(8))
    delete_command_after = Column(Boolean, default=True)
    deactivate_modules = relationship('DeactivateModule')
