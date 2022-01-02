from vkwave.bots import SimpleLongPollUserBot, TaskManager

from utils import config, database_init, set_my_id
from utils import Middleware
from commands import routers


bot = SimpleLongPollUserBot(config['VK']['user_token'])


bot.add_middleware(Middleware())

for router in routers:
    if config['commands'][router.name]:
        bot.dispatcher.add_router(router)
        print(f'{router.name} роутер успешно добавлен!')
        continue
    print(f'{router.name} роутер отключен.')


tasks = TaskManager()
tasks.add_task(set_my_id(bot.api_context))
tasks.add_task(database_init())
tasks.add_task(bot.run())
print('Бот успешно запущен!')
tasks.run()
