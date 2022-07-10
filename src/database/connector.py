from tortoise import Tortoise


async def connect_database(database_url: str):
    await Tortoise.init(
        db_url=database_url,
        modules={'models': ['src.database.models']}
    )
    await Tortoise.generate_schemas()
