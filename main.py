import logging
import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# Импорт всех роутеров
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.admin import router as admin_router

# Загружаем переменные окружения из .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    # Подключаем все роутеры
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(admin_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("🚀 Запуск ресторанного бота...")
    asyncio.run(main())