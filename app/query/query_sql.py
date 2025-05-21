import asyncio
from itertools import product

from aiogram import types, BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.config import logger
from database.database import engine, async_session_maker
from models.models import User, Profile, Category, Product

# декоратор для сессий
def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                # Явно не открываем транзакции, так как они уже есть в контексте
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()  # Откатываем сессию при ошибке
                raise e  # Поднимаем исключение дальше
            finally:
                await engine.dispose()  # Закрываем сессию

    return wrapper



@connection
async def reg_user(telegram_id: int,
                        username:str,first_name:str,last_name:str,session):
    try:
        result = await session.execute(select(User).filter_by(telegram_id=telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            new_user = User(
                telegram_id = telegram_id,
                username = username,
                first_name = first_name,
                last_name = last_name
            )
            session.add(new_user)
            await session.flush()

            new_profile = Profile(
                user_id = new_user.id,
                first_name = first_name,
                last_name =last_name
            )
            session.add(new_profile)
            await session.commit()
    except IntegrityError:
        await session.rollback()
    finally:
        await engine.dispose()  # Закрываем сессию

@connection
async def get_user_profile(telegram_id: int, session):
    logger.info(f"Попытка получить профиль пользователя с Telegram ID: {telegram_id}")
    result = await session.execute(select(User).filter(User.telegram_id == telegram_id))
    user_profile = result.scalar_one_or_none()

    if user_profile:
        logger.info(f"Профиль пользователя найден: {user_profile.username}")
    else:
        logger.info("Профиль пользователя не найден.")

    return user_profile







@connection
async def get_product_price(product_id, session):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    return product.price if product else None


@connection
async def get_product_link(product_id, session):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    return product


@connection
async def deduct_stars(user_id: int, stars: int, session):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user and user.stars >= stars:
        user.stars -= stars
        await session.commit()
        return True
    return False






@connection
async def get_category(session):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    return categories




@connection
async def get_products_by_category(category_id,session):
    result = await session.execute(select(Product).where(Product.category_id == category_id))
    products = result.scalars().all()
    return products



