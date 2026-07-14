import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Отримуємо токени з налаштувань сервера (Render)
TOKEN = os.getenv('TOKEN')
MAXELPAY_API_KEY = os.getenv('MAXELPAY_API_KEY')

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Вітаю! Я готовий до роботи. Натисни /pay для створення інвойсу.")

async def main():
    print("Бот запущений і чекає на повідомлення!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())