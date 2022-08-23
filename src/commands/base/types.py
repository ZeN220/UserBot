from enum import IntEnum
from typing import Dict

from pydantic import BaseModel, Field, validator


class Priority(IntEnum):
    LOW = 10
    MEDIUM = 50
    HIGH = 100


class CommandResponse(BaseModel):
    response: str = Field(None, description='Answer of command')


class CommandArgs(BaseModel):
    args: Dict[str, str]

    @validator('args')
    def convert_arg_to_int(cls, args: Dict[str, str]):  # noqa
        """
        Из-за того, что re.Pattern.groupdict() не возвращает значения словаря в виде числа,
        пришлось создать модель для аргументов и валидировать значения в ней
        """
        for key, value in args.items():
            if value.isdigit():
                args.update({key: int(value)})
        return args
