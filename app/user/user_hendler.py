from gc import callbacks
from random import randint

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import logger
from app.query.query_sql import reg_user, get_user_profile, get_category, get_products_by_category, connection
from app.user.kb_user import ease_link_kb

user_router = Router()


@user_router.message(Command('start'))
async def start(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    logger.info(f"Registering user: {telegram_id}, {username}, {first_name}, {last_name}")
    await reg_user(telegram_id=telegram_id, username=username, first_name=first_name,
                        last_name=last_name)

    await message.answer('Добро пожаловать',reply_markup=ease_link_kb())


@user_router.message(lambda message: message.text == 'Профиль')
async def get_person(message: types.Message):
    user_id = message.from_user.id
    user_profile = await get_user_profile(user_id)

    if user_profile:
        profile_info = (
            f"👤 Профиль:\n"
            f"<b>ID</b>: {user_profile.telegram_id}\n"
            f"<b>Логин:</b>:  {user_profile.username}\n"
            f"<b>Имя</b>: {user_profile.first_name}\n"
            f"<b>Фамилия</b>: {user_profile.last_name}\n"
        )
        await message.answer(profile_info)

   # for category in categories:
    #     inline_kb.append([InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")])
    # keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)

# ,callbacks=f'category_{i.id}


@user_router.message(lambda message: message.text == 'Категории')
async def category(message: types.Message):
    categories = await get_category()
    kb = []
    for category in categories:
        kb.append([InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("Выберите категорию:", reply_markup=keyboard)



from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@user_router.callback_query(lambda c: c.data and c.data.startswith('category_'))
async def process_category(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split('_')[1])
    await callback_query.answer(f"Вы выбрали категорию: {category_id}")

    products = await get_products_by_category(category_id=category_id)
    if products:
        for product in products:
            # Создаем инлайн-кнопку для оплаты
            payment_button = InlineKeyboardButton(
                text=f"Оплатить {product.price}",
                url="https://your-payment-provider-link.com"  # Замените на реальную ссылку для оплаты
            )

            # Создаем клавиатуру с кнопкой
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[payment_button]])

            await callback_query.message.answer(
                f"<b>{product.name}</b>\n"
                f"{product.Description}\n"
                f"Цена: {product.price}",
                reply_markup=keyboard
            )
    else:
        await callback_query.message.answer("В этой категории нет продуктов.")








