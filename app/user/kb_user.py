# Создание инлайн-кнопок
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup




def ease_link_kb():
    kb = [
        [KeyboardButton(text='👥Профиль')],
        [KeyboardButton(text='📒Категории')],
        [KeyboardButton(text='✉Тех. поддержка')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard






