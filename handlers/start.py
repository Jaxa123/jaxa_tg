from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_keyboard import get_main_keyboard

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"👋 Hello, {message.from_user.full_name}!\n"
        f"Welcome to our Restaurant Bot!\n\n"
        f"I can help you:\n"
        f"🍽️ Browse our menu\n"
        f"📞 Get contact information\n"
        f"📍 Find our location\n"
        f"⏰ Check opening hours",
        reply_markup=get_main_keyboard()
    )