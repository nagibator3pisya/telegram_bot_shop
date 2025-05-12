from gc import callbacks
from random import randint

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton, \
    ReplyKeyboardMarkup, LabeledPrice
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import logger
from app.query.query_sql import reg_user, get_user_profile, get_category, get_products_by_category, deduct_stars, \
    get_product_price
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






from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@user_router.callback_query(lambda c: c.data and c.data.startswith('category_'))
async def process_category(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split('_')[1])
    await callback_query.answer(f"Вы выбрали категорию: {category_id}")

    products = await get_products_by_category(category_id=category_id)
    if products:
        for product in products:
            # Создаем инлайн-кнопку для оплаты звездами
            payment_button = InlineKeyboardButton(
                text=f"Оплатить {product.price} ⭐️",
                callback_data=f"pay_stars_{product.id}"
            )
            # Создаем инлайн-кнопку для тестового платежа
            test_payment_button = InlineKeyboardButton(
                text="Тестовый платеж",
                callback_data=f"test_payment_{product.id}"
            )
            # Создаем клавиатуру с кнопкой
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[payment_button], [test_payment_button]])

            await callback_query.message.answer(
                f"<b>{product.name}</b>\n"
                f"{product.Description}\n"
                f"Цена: {product.price} ⭐️",
                reply_markup=keyboard
            )
    else:
        await callback_query.message.answer("В этой категории нет продуктов.")




@user_router.callback_query(lambda c: c.data and c.data.startswith('pay_stars_'))
async def process_star_payment(callback_query: types.CallbackQuery):
    product_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id

    product_price = await get_product_price(product_id)

    if product_price is not None:
        # Проверяем, достаточно ли звезд у пользователя
        if await deduct_stars(user_id, product_price):
            await callback_query.answer(f"Вы успешно оплатили {product_price} ⭐️!")
        else:
            await callback_query.answer("У вас недостаточно звезд для оплаты.")
    else:
        await callback_query.answer("Не удалось получить информацию о продукте.")


@user_router.callback_query(lambda c: c.data and c.data.startswith('test_payment_'))
async def process_test_payment(callback_query: types.CallbackQuery):
    product_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id

    # Отправляем тестовый счет
    prices = [LabeledPrice(label="Test Payment", amount=2000)]  # Сумма в минимальных единицах валюты
    await callback_query.message.answer_invoice(
        title="Тестовый платеж",
        description="Описание тестового платежа",
        prices=prices,
        provider_token="",  # Замените на ваш тестовый токен
        payload=f"test_payment_{product_id}",
        currency="XTR",  # Используйте поддерживаемую валюту
    )


