from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.config import logger
from app.query.query_sql import reg_user, get_user_profile, get_category
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


@user_router.message(lambda message: message.text == 'Профиль')
async def get_person(message: types.Message, session):
    user_id = message.from_user.id
    user_profile = await get_user_profile(user_id, session)

    if user_profile:
        profile_info = (
            f"👤 Профиль:\n"
            f"<b>ID</b>: {user_profile.telegram_id}\n"
            f"<b>Логин:</b>:  {user_profile.username}\n"
            f"<b>Имя</b>: {user_profile.first_name}\n"
            f"<b>Фамилия</b>: {user_profile.last_name}\n"
        )
        await message.answer(profile_info)




@user_router.message(lambda message: message.text == 'Категории')
async def category(message: types.Message, session):
    categories = await get_category(session=session)

    # список строк с кнопками
    inline_kb = []
    for category in categories:
        inline_kb.append([InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")])

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@user_router.callback_query(text = 'category_')
async def callback_category():
    pass