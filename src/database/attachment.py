from typing import Optional, List

from sqlalchemy import Integer, Text, Column, ForeignKey

from .base import Base


class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(ForeignKey('templates.id'), index=True)
    document = Column(Text)
