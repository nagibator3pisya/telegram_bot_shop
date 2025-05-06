import asyncio

from aiogram import types
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import bd, bot, logger
from app.query.query_sql import reg_user, DatabaseMiddleware


bd.message.middleware(DatabaseMiddleware())


#### Регистрация пользователя как только он ввёл старт


@bd.message(Command('start'))
async def start(message: types.Message ,session):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    logger.info(f"Registering user: {telegram_id}, {username}, {first_name}, {last_name}")
    await reg_user(session=session,telegram_id=telegram_id, username=username, first_name=first_name,
                        last_name=last_name)

    await message.answer('Добро пожаловать!')



async def main():
    await bd.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())