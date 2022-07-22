from .base import BaseHandler, CommandManager, CommandResponse


@CommandManager.register(
    name='test', module='social', aliases=['test', 'тест'],
    priority=10, pattern='',
)
class TestHandler(BaseHandler):
    async def execute(self) -> CommandResponse:
        return CommandResponse(response='123')
