# Создание инлайн-кнопок
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.query.query_sql import get_user_profile


def ease_link_kb():
    kb = [
        [types.KeyboardButton('Профиль') ],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb,resize_keyboard=True)
    return keyboard



# async def get_person(session,message: types.Message):
#     user_id = message.from_user.id
#     user_profile = await get_user_profile(user_id, session)
#
#     if user_profile:
#         profile_info = (
#             f"Профиль:\n"
#             f"ID: {user_profile.id}\n"
#             f"Telegram ID: {user_profile.telegram_id}\n"
#             f"Username: {user_profile.username}\n"
#             f"First Name: {user_profile.first_name}\n"
#             f"Last Name: {user_profile.last_name}\n"
#         )
#         await message.answer(profile_info)
#     else:
#         await message.answer("Профиль не найден.")
