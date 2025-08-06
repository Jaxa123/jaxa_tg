import logging
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '8181220707:AAHt03llUwCNthyHDqbAwFz3X7oagdHagDM'

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я ресторанный бот.")

if __name__ == '__main__':
    logger.info("🚀 Запуск ресторанного бота...")
    executor.start_polling(dp, skip_updates=True)