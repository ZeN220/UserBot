from .base import CommandResponse
from .develop import GetPeerIDHandler, GetUserIDHandler, GetMessageIDHandler, GetMessageJSONHandler
from .dialogs import ReadDialogsHandler
from .social import AddFriendHandler, RemoveBlockHandler, RemoveFriendHandler, AddBlockHandler, \
    InviteHandler
from .templates import AddTemplateHandler, GetTemplatesHandler, DeleteTemplateHandler
