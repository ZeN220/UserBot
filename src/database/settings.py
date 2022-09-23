from sqlalchemy import Column, Integer, String, JSON

from .base import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer)
    name = Column(String)
    value = Column(JSON)
