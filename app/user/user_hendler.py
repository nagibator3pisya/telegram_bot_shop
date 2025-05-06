from aiogram import types, Router
from aiogram.filters import Command

from app.config import logger
from app.query.query_sql import reg_user

user_router = Router()

@user_router.message(Command('start'))
async def start(message: types.Message ,session):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    logger.info(f"Registering user: {telegram_id}, {username}, {first_name}, {last_name}")
    await reg_user(session=session,telegram_id=telegram_id, username=username, first_name=first_name,
                        last_name=last_name)

    await message.answer('Добро пожаловать!')