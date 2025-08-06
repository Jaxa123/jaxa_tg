from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽️ Menu", callback_data="menu"),
            InlineKeyboardButton(text="📞 Contact", callback_data="contact")
        ],
        [
            InlineKeyboardButton(text="📍 Location", callback_data="location"),
            InlineKeyboardButton(text="⏰ Hours", callback_data="hours")
        ]
    ])
    return keyboard