import time

from vkwave.api import APIOptionsRequestContext

from .base import command_manager, CommandResponse, BaseHandler, Priority

execute_code = """
var dialogs = API.messages.getConversations({"count": 200, "filter": "unread"}).items;
var iter_list = dialogs;
var calls = 1;
while(iter_list.length > 0 && calls < 25) { 
    var dialog = iter_list.pop();
    API.messages.markAsRead({"peer_id": dialog.conversation.peer.id});
    calls = calls + 1;
}
return dialogs;
"""


@command_manager.register(
    name='read_dialogs', module='dialogs',
    aliases=['read', 'чтение'], priority=Priority.MEDIUM
)
class ReadDialogsHandler(BaseHandler):
    async def execute(self, api_context: APIOptionsRequestContext) -> 'CommandResponse':
        start_time = time.time()
        await read_all_dialogs(api_context)
        result = time.time() - start_time
        return CommandResponse(
            response=f'[📭] Диалоги успешно прочитаны за {result:.3f} секунд.'
        )


async def read_all_dialogs(api_context: APIOptionsRequestContext) -> None:
    """
    Из-за того, что VK API возвращает максимум 200 диалогов за 1 запрос,
    нужно рекурсивно вызывать метод чтения диалогов.
    """
    dialogs = await _read_dialogs(api_context)
    while dialogs:
        dialogs = await _read_dialogs(api_context)


async def _read_dialogs(api_context: APIOptionsRequestContext):
    result = await api_context.execute(code=execute_code)
    return result.response
