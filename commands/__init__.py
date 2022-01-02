from commands.qiwi.get_balance import qiwi_balance_router
from commands.qiwi.payment import qiwi_payment_router
from commands.to_delete import to_delete_router
from commands.message import messages_router
from commands.logger import logger
from commands.social import social_router
from commands.dev import dev_router


routers = [
    to_delete_router, social_router, dev_router,
    messages_router, qiwi_balance_router, qiwi_payment_router,
    logger
]
