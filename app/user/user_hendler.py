from gc import callbacks
from random import randint

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, KeyboardButton, \
    ReplyKeyboardMarkup, LabeledPrice, PreCheckoutQuery, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import logger
from app.query.query_sql import reg_user, get_user_profile, get_category, get_products_by_category, deduct_stars, \
    get_product_price, get_product_link
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


@user_router.message(lambda message: message.text == '👥Профиль')
async def get_person(message: types.Message):
    telegram_id = message.from_user.id
    user_profile = await get_user_profile(telegram_id)

    if user_profile:
        profile_info = (
            f"👤 Профиль:\n"
            f"<b>ID</b>: {user_profile.telegram_id}\n"
            f"<b>Логин:</b>  {user_profile.username}\n"
            f"<b>Имя</b>: {user_profile.first_name}\n"
            f"<b>Фамилия</b>: {user_profile.last_name}\n"
        )
        await message.answer(profile_info, parse_mode=ParseMode.HTML)
    else:
        await message.answer("Профиль не найден.")

@user_router.message(lambda message: message.text == '✉Тех. поддержка')
async def administrator(message: types.Message):
    await message.answer(f'Если у вас остались вопросы по покупке, обращайтесь к администратору @Extosik')


@user_router.message(lambda message: message.text == '📒Категории')
async def category(message: types.Message):
    categories = await get_category()
    kb = []
    for category in categories:
        kb.append([InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@user_router.callback_query(lambda c: c.data and c.data.startswith('category_'))
async def process_category(callback_query: types.CallbackQuery):
    category_id = int(callback_query.data.split('_')[1])
    await callback_query.answer(f"Вы выбрали категорию: {category_id}")

    products = await get_products_by_category(category_id=category_id)
    if products:
        for product in products:
            keyboard = await price(product.id)
            await callback_query.message.answer(
                f"🤭{product.name}🤭\n"
                f"🥵{product.Description}🥵\n",
                reply_markup=keyboard, parse_mode=ParseMode.HTML
            )
    else:
        await callback_query.message.answer("В этой категории нет продуктов.")

async def price(product_id: int) -> InlineKeyboardMarkup:
    product = await get_product_link(product_id)  # Получаем продукт по ID
    if product:
        payment_button = InlineKeyboardButton(
            text=f"Оплатить {product.price} ⭐️",
            callback_data=f"pay_stars_{product.id}",
            pay=True
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[[payment_button]])
        return keyboard
    return None















@user_router.callback_query(lambda c: c.data and c.data.startswith('pay_stars_'))
async def process_star_payment(callback_query: types.CallbackQuery):
    data = callback_query.data.split('_')
    product_id = int(data[2])
    user_id = callback_query.from_user.id

    product_price = await get_product_price(product_id)

    prices = [LabeledPrice(label="XTR", amount=product_price)]

    await callback_query.message.answer_invoice(
        title='Покупка',
        description=f'Наш продукт принесет вам большую радость:)',
        prices=prices,
        provider_token="",
        payload=f"pay_stars_{product_id}",
        currency="XTR"
    )



@user_router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

async def successful_payment_handler(message: Message):
    payload = message.successful_payment.invoice_payload
    product_id = int(payload.split('_')[2])
    product = await get_product_link(product_id)
    if product and product.private_link:
        await message.answer(f"Спасибо за покупку! Вот ваша ссылка: {product.private_link}")
    else:
        await message.answer("Спасибо за покупку! К сожалению, ссылка на ресурс недоступна.")







