from gc import callbacks
from random import randint

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton, \
    ReplyKeyboardMarkup, LabeledPrice, PreCheckoutQuery, Message
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




@user_router.message(lambda message: message.text == 'Категории')
async def category(message: types.Message):
    categories = await get_category()
    kb = []
    for category in categories:
        kb.append([InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("Выберите категорию:", reply_markup=keyboard)



async def price(category_id: int) -> InlineKeyboardMarkup:
    products = await get_products_by_category(category_id=category_id)
    if products:
        for product in products:
            # Создаем инлайн-кнопку для оплаты звездами
            # payment_button = InlineKeyboardButton(
            #     text=f"Оплатить {product.price} ⭐️",
            #     callback_data=f"pay_stars_{product.id}_{category_id}",  # Включите category_id в данные обратного вызова
            #     pay=True
            # )
            # Создаем инлайн-кнопку для тестового платежа
            test_payment_button = InlineKeyboardButton(
                text="Тестовый платеж",
                callback_data=f"test_payment_{product.id}"
            )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[test_payment_button]])
            return keyboard
    return None


@user_router.callback_query(lambda c: c.data and c.data.startswith('category_'))
async def process_category(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split('_')[1])
    await callback_query.answer(f"Вы выбрали категорию: {category_id}")

    products = await get_products_by_category(category_id=category_id)
    if products:
        for product in products:
            keyboard = await price(category_id)
            await callback_query.message.answer(
                f"<b>{product.name}</b>\n"
                f"{product.Description}\n",
                reply_markup=keyboard
            )
    else:
        await callback_query.message.answer("В этой категории нет продуктов.")




# @user_router.callback_query(lambda c: c.data and c.data.startswith('pay_stars_'))
# async def process_star_payment(callback_query: types.CallbackQuery):
#     data = callback_query.data.split('_')
#     product_id = int(data[2])
#     user_id = callback_query.from_user.id
#
#     product_price = await get_product_price(product_id)
#     prices = [LabeledPrice(label="XTR", amount=product_price)]
#
#     await callback_query.message.answer_invoice(
#         title='Покупка',
#         description='Приобретение товара',
#         prices=prices,
#         provider_token="",
#         payload=f"pay_stars_{product_id}",
#         currency="XTR"
#     )

@user_router.callback_query(lambda c: c.data and c.data.startswith('test_payment_'))
async def process_test_payment(callback_query: types.CallbackQuery):
    product_id = int(callback_query.data.split('_')[2])
    user_id = callback_query.from_user.id

    # Отправляем тестовый счет
    prices = [LabeledPrice(label="Test Payment", amount=1)]  # Сумма в минимальных единицах валюты
    await callback_query.message.answer_invoice(
        title="Тестовый платеж",
        description="Описание тестового платежа",
        prices=prices,
        provider_token="unique_invoice_payload",
        payload=f"test_payment_{product_id}",
        currency="XTR",
    )

@user_router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    # Логика для предварительной проверки платежа
    await pre_checkout_query.answer(ok=True)

async def successful_payment_handler(message: Message):
    await message.answer("Спасибо за тестовый платеж!")





#     )


