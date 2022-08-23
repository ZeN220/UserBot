from sqlalchemy import Column, Text, ForeignKey, Integer

from .base import Base


class DeactivateModule(Base):
    __tablename__ = 'deactivate_modules'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    module = Column(Text)
    session_owner_id = Column(ForeignKey('sessions.owner_id'), index=True)
