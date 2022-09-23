from .chats import chats_module
from .develop import develop_module
from .dialogs import dialogs_module
from .social import social_module
from .templates import templates_module
from .session import session_module
from .base.manager import ModulesManager


def setup_modules(modules_manager: ModulesManager):
    modules_manager.add_module(develop_module)
    modules_manager.add_module(dialogs_module)
    modules_manager.add_module(social_module)
    modules_manager.add_module(templates_module)
    modules_manager.add_module(chats_module)
    modules_manager.add_module(session_module)
    modules_manager.sort_modules()
