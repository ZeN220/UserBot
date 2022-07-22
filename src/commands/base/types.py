from enum import IntEnum

from pydantic import BaseModel, Field


class Priority(IntEnum):
    LOW = 10
    MEDIUM = 50
    HIGH = 100


class CommandResponse(BaseModel):
    response: str = Field(None, description='Answer of command')
