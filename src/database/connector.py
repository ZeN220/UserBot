import logging

from tortoise.exceptions import DBConnectionError
from tortoise import Tortoise

logger = logging.getLogger(__name__)


async def connect_database(database_url: str):
    try:
        await Tortoise.init(
            db_url=database_url,
            modules={'models': ['src.database.models']}
        )
        await Tortoise.generate_schemas()
        logger.debug(f'База данных {database_url} успешно подключена.')
    except DBConnectionError:
        logger.error(f'При попытке подключения к {database_url} произошла ошибка.')
