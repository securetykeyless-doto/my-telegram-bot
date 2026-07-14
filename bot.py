import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

# Налаштування
TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('MAXELPAY_API_KEY')
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Стани
class Order(StatesGroup):
    waiting_for_contact = State()
    waiting_for_address = State()

# 1. Функція створення інвойсу через API MaxelPay
async def create_invoice(amount, user_id):
    url = "https://api.maxelpay.com/invoices" # Перевірте правильність URL у доці
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {"amount": amount, "currency": "USD", "description": f"Замовлення від {user_id}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            return data.get('payment_url')

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привіт! Натисніть /pay для оплати.")

@dp.message(Command("pay"))
async def pay(message: types.Message, state: FSMContext):
    link = await create_invoice(10.00, message.from_user.id)
    await message.answer(f"Ось ваше посилання: {link}\nПісля оплати напишіть ваш номер телефону.")
    await state.set_state(Order.waiting_for_contact)

@dp.message(Order.waiting_for_contact)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Дякую! Тепер надішліть адресу доставки.")
    await state.set_state(Order.waiting_for_address)

# Webhook для MaxelPay (потрібен для отримання сповіщень про оплату)
async def handle_webhook(request):
    data = await request.json()
    # Логіка обробки оплати (наприклад, перевірка статусу)
    return web.Response(status=200)

# Запуск
if __name__ == "__main__":
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    # Потрібно запускати і бота, і веб-сервер одночасно
    # (Це просунутий крок, почнемо з перевірки `/pay`)
