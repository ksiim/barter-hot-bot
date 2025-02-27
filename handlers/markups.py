from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from bot import bot

from .callbacks import *


async def generate_start_text(message):
    return f"Привет, {message.from_user.full_name}! Я - бот, который поможет обменять твою недвижимость. Нажми на кнопку ниже, чтобы добавить свою недвижимость."

start_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="Начать",
            callback_data='go'
        )]
    ]
)

phone_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="Отправить номер телефона",
                request_contact=True,
            )
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

form_doc_file_id = 'BQACAgIAAxkBAAICLGe9abrN9VSZsGWbOTUvT-QAATR5bAAC1mcAArVt6UlwQaIEJEC-SjYE'

start_photo_file_id = 'AgACAgIAAxkBAAID7WfAeqARRwtXz-avhP85-frdH6yoAAIK9DEbtW3xSeP4vYR5c7puAQADAgADeQADNgQ'
