from random import randint

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import logger
from app.query.query_sql import reg_user, get_user_profile, get_category, get_products_by_category
from app.user.kb_user import ease_link_kb

user_router = Router()


@user_router.message(Command('start'))
async def start(message: types.Message, session):
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
        inline_kb.append([InlineKeyboardButton(text=category.name, callback_data=f"category_")])

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@user_router.callback_query(lambda call: call.data.startswith('category_'))
async def process_category(callback_query: CallbackQuery, session):
    category_id = int(callback_query.data.split('_')[1])
    products = await get_products_by_category(session=session, category_id=category_id)
    response = "Продукты в выбранной категории:\n"
    for product in products:
        response += f"{product.name}\n"

    await callback_query.answer()
    await callback_query.message.answer(response)



