from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

remove = ReplyKeyboardRemove()

empty_inline = InlineKeyboardMarkup(inline_keyboard=[])

phone_number = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Telefon raqam yuborish", request_contact=True)]],
    resize_keyboard=True,
    input_field_placeholder="Telefon raqamingizni yuboring ☎️",
)


async def choose_day():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Bugun", callback_data="day_current")],
            [InlineKeyboardButton(text="Ertaga", callback_data="day_tomorrow")],
        ]
    )


async def tables(tables: list):
    keyboard = InlineKeyboardBuilder()
    for table in tables:
        keyboard.add(
            InlineKeyboardButton(text=table[1], callback_data=f"table_{table[0]}")
        )
    return keyboard.adjust(3).as_markup()
