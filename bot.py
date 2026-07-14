import os
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('MAXELPAY_API_KEY')
# Ваш webhook URL з Render
WEBHOOK_URL = "https://my-telegram-bot-zqlr.onrender.com/webhook"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Order(StatesGroup):
    waiting_for_contact = State()

async def create_maxelpay_session(order_id, amount):
    url = "https://api.maxelpay.com/api/v1/payments/sessions"
    headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        "orderId": order_id,
        "amount": float(amount),
        "currency": "USD",
        "description": "Покупка в боті",
        "successUrl": "https://t.me/VinToPin_bot", # Замініть на свій нік бота
        "callbackUrl": WEBHOOK_URL
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            return data.get('data', {}).get('paymentUrl')

@dp.message(Command("pay"))
async def pay_handler(message: types.Message, state: FSMContext):
    # Генеруємо унікальний ID замовлення на основі ID користувача та часу
    order_id = f"ORDER-{message.from_user.id}"
    link = await create_maxelpay_session(order_id, 10.00) # Наприклад, 10 USD
    
    if link:
        await message.answer(f"Посилання на оплату: {link}\nПісля оплати напишіть свій номер телефону.")
        await state.set_state(Order.waiting_for_contact)
    else:
        await message.answer("Сталася помилка при створенні платежу.")

@dp.message(Order.waiting_for_contact)
async def get_phone(message: types.Message, state: FSMContext):
    await message.answer(f"Дякую! Ваш номер {message.text} отримано. Очікуємо підтвердження оплати.")
    await state.clear()

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
