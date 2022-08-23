from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.orm import relationship

from .base import Base


class Template(Base):
    __tablename__ = 'templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger = Column(String(64), index=True)
    answer = Column(Text, nullable=True)
    owner_id = Column(Integer, index=True)
    attachments = relationship('Attachment')
