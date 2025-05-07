from aiogram import Router, types
from aiogram.filters import Command

from app.config import logger
from app.query.query_sql import reg_user, get_user_profile
from app.user.kb_user import ease_link_kb

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

    await message.answer('Добро пожаловать',reply_markup=ease_link_kb())


async def profile(message: types.Message, session):
    user_id = message.from_user.id
    user_profile = await get_user_profile(user_id, session)
    profile_info = (
        f"Профиль:\n"
        f"ID: {user_profile.id}\n"
        f"Telegram ID: {user_profile.telegram_id}\n"
        f"Username: {user_profile.username}\n"
        f"First Name: {user_profile.first_name}\n"
        f"Last Name: {user_profile.last_name}\n"
        )
    await message.answer(profile_info)


@user_router.message(lambda message: message.text == 'Профиль')
async def handle_profile_button(message: types.Message):
    profile_data = profile()
    await message.reply(profile_data)
