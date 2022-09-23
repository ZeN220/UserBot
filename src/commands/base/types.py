from enum import IntEnum
from typing import Dict, Optional

from pydantic import BaseModel, Field, validator


class Priority(IntEnum):
    LOW = 10
    MEDIUM = 50
    HIGH = 100


class CommandResponse(BaseModel):
    code: int = Field(200, description='Command execution code')
    response: str = Field(None, description='Answer of command')


class CommandArgs(BaseModel):
    args: Dict[str, Optional[str]]

    @validator('args')
    def convert_arg_to_int(cls, args: Dict[str, str]):  # noqa
        """
        Из-за того, что re.Pattern.groupdict() не возвращает значения словаря в виде числа,
        пришлось создать модель для аргументов и валидировать значения в ней
        """
        for key, value in args.items():
            value = value.lower()
            if value is None:
                continue
            elif value.isdigit():
                value = int(value)
            elif value == 'true':
                value = True
            elif value == 'false':
                value = False
            args.update({key: value})
        return args
