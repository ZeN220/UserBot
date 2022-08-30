import logging
from typing import List, Optional

from .command import Command
from src.sessions import Session
from .module import Module

logger = logging.getLogger(__name__)


class ModulesManager:
    def __init__(self):
        self.modules: List[Module] = []

    def find_command(self, session: Session, text: str) -> Optional[Command]:
        for module in self.modules:
            if module.name in session.deactivate_modules:
                continue
            command = module.get_command(text)
            if command:
                return command

    def add_module(self, module: Module):
        self.modules.append(module)
