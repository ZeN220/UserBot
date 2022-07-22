from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import CommandResponse


class BaseHandler(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> 'CommandResponse':
        ...
