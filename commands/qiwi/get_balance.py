from vkwave.bots import (
    simple_user_message_handler,
    FromMeFilter,
    LevenshteinFilter,
    SimpleUserEvent
)

from utils import config, Router, bot


qiwi_balance_router = Router(
    'get_balance',
    'Команда для получение баланса с указанного QIWI кошелька.'
)


@simple_user_message_handler(
    qiwi_balance_router,
    LevenshteinFilter(['.qbalance'], 2),
    FromMeFilter(True)
)
async def qiwi_balance(event: SimpleUserEvent):
    client = event.api_ctx.api_options.get_client().http_client
    # Установка заголовка с апи ключом QIWI, для получения баланса
    headers = {
        'Accept': 'application/json',
        'authorization': f'Bearer {config["qiwi"]["qiwi_token"]}'
    }
    phone = config["qiwi"]["qiwi_phone"]
    qiwi_get = await client.raw_request(
        url=f'https://edge.qiwi.com/funding-sources/v2/persons/{phone}/accounts',
        headers=headers,
        method='get'
    )
    balance = (await qiwi_get.json())['accounts'][0]['balance']['amount']
    # Разбивка числа на разряды для читаемости
    balance = f'{balance:,}'.replace(',', ' ')
    await bot.api_context.messages.send(
        message=f'[🥝] Ваш баланс на кошельке QIWI составляет -- '
                f'{balance.replace(".", ",")} рублей!',
        peer_id=config['VK']['user_id'],
        random_id=0
    )
