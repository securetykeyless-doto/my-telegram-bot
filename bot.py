import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('MAXELPAY_API_KEY')
ADMIN_ID = 7749452087 # Вставте сюди ВАШ ID в телеграм (дізнатися можна через @userinfobot)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Order(StatesGroup):
    waiting_for_payment = State()
    waiting_for_vin = State()

# --- СТАРТОВЕ ПОВІДОМЛЕННЯ ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Welcome to our service! 🚗\n\n"
        "We specialize in professional automotive solutions for European customers. "
        "Our process is transparent, secure, and fast.\n\n"
        "1. Select your service.Hundai VIN to PIN\n"
        "2. Complete the secure cryptocurrency payment via MaxelPay.\n"
        "3. Provide your VIN number for processing.\n"
        "4. Receive your access PIN-code instantly.15-60 min.\n\n"
        "Press /pay to start your order."
    )

@dp.message(Command("pay"))
async def pay_handler(message: types.Message, state: FSMContext):
    order_id = f"ORDER-{message.from_user.id}"
    # Тут ви можете змінити суму PRICE
    link = await create_maxelpay_session(order_id, 4.00) 
    
    await message.answer(f"Please complete your payment here:\n{link}\n\nAfter payment, click the button below:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="I have paid", callback_data="check_payment")]
        ]))
    await state.set_state(Order.waiting_for_payment)

@dp.callback_query(F.data == "check_payment")
async def check_payment(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Payment confirmed! Now please enter your VIN number.")
    await state.set_state(Order.waiting_for_vin)

@dp.message(Order.waiting_for_vin)
async def get_vin(message: types.Message, state: FSMContext):
    vin = message.text
    # Повідомляємо вам (адміну)
    await bot.send_message(ADMIN_ID, f"New order from {message.from_user.id} (@{message.from_user.username}).\nVIN: {vin}")
    await message.answer("VIN received! Processing... Please wait for your PIN-code.")
    await state.clear()

# --- ВІДПОВІДЬ КЛІЄНТУ ---
# Використовуйте команду /reply [ID_клієнта] [PIN]
@dp.message(Command("reply"))
async def reply_to_client(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        args = message.text.split()
        client_id = args[1]
        pin = args[2]
        await bot.send_message(client_id, f"Your PIN-code is: {pin}")
        await message.answer("PIN sent successfully.")

async def create_maxelpay_session(order_id, amount):
    url = "https://api.maxelpay.com/api/v1/payments/sessions"
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    payload = {"orderId": order_id, "amount": float(amount), "currency": "USD", "description": "VIN to PIN"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            return data.get('data', {}).get('paymentUrl')

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
