from aiogram import types, BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.config import logger
from database.database import engine, async_session_maker
from models.models import User, Profile, Category


# на всякий случай изучить как работает
class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict
    ) -> any:
        async with async_session_maker() as session:
            data["session"] = session
            return await handler(event, data)




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


async def get_user_profile(user_id: int, session):
    logger.info(f"Fetching profile for user_id: {user_id}")
    result = await session.execute(select(User).filter(User.id))
    user_profile = result.scalar_one_or_none()
    logger.info(f"User profile found: {user_profile}")
    return user_profile



async def get_category(session):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    return categories