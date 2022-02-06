from dataclasses import dataclass
import random
import time

from vkwave.bots.storage.types import Key
from vkwave.http import AbstractHTTPClient
from vkwave.bots import (
    TTLStorage,
    UserEvent,
    FromMeFilter,
    TextStartswithFilter,
    MessageArgsFilter
)
from aiogram import Bot

from utils import send_message_to_me, config
from dispatching import Router


storage = TTLStorage(60)
qiwi_payment_router = Router(
    __name__,
    'Команда для отправки платежа на QIWI кошелек и его подтверждения'
)
qiwi_payment_router.registrar.add_default_filter(FromMeFilter(True))

if config['commands']['payment']:
    aiogram = Bot(token=config['telegram']['telegram_bot_token'])


@dataclass
class PaymentData:
    phone: str
    amount: int
    comment: str


async def payment(data: PaymentData, client: AbstractHTTPClient):
    headers = {
        'Accept': 'application/json',
        'authorization': f'Bearer {config["qiwi"]["qiwi_token"]}'
    }
    json_body = {
        "id": str(int(time.time() * 1000)),
        "sum": {
            "amount": data.amount,
            "currency": '643'
        },
        "paymentMethod": {
            "type": 'Account',
            "accountId": '643'
        },
        "comment": data.comment or '',
        "fields": {
            "account": data.phone
        }
    }
    pay = await client.raw_request(
        url='https://edge.qiwi.com/sinap/api/v2/terms/99/payments',
        json=json_body,
        headers=headers,
        method='post'
    )
    return await pay.json()


@qiwi_payment_router.message_handler(
    TextStartswithFilter('.qpay')
)
async def qiwi_payment(event: UserEvent):
    text = event.object.object.text.split()
    if len(text) >= 3:
        payment_data = PaymentData(text[1], int(text[2]), ' '.join(text[3:]))
        # Создание кода для подтверждения платежа
        code = ''.join(random.sample('123456789', 6))
        if config['qiwi']['2fa_payment']:
            # Запись телефона, сумму платежа и его код в хранилище
            await storage.put(Key(str(code)), payment_data)
            await aiogram.send_message(
                text=f'Ваш код для подтверждения платежа на QIWI кошелёк: {code}',
                chat_id=config['telegram']['telegram_id']
            )
            await send_message_to_me(
                message='[🥝] Отправлен код подтверждения платежа. '
                        'Ожидается ввод.',
                peer_id=config['VK']['user_id'],
                random_id=0
            )

        else:
            await send_message_to_me(
                message='[🥝] Отправляю перевод...',
                peer_id=config['VK']['user_id'],
                random_id=0
            )
            await payment(
                payment_data, event.api_ctx.api_options.get_client().http_client
            )


@qiwi_payment_router.message_handler(
    TextStartswithFilter('.code'),
    MessageArgsFilter(1)
)
async def qiwi_code(event: UserEvent):
    input_code = event.object.object.text.split()[1]
    # Получение данных для платежа
    payment_data = await storage.get(Key(input_code), None)

    if payment_data:
        await send_message_to_me(
            message='[🥝] Код введён верно! Отправляю перевод...',
            peer_id=config['VK']['user_id'],
            random_id=0
        )
        await payment(
            payment_data, event.api_ctx.api_options.get_client().http_client
        )

    else:
        await send_message_to_me(
            message='[🥝] Вы ввели неправильный код подтверждения.',
            peer_id=config['VK']['user_id'],
            random_id=0
        )
