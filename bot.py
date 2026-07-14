import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

# --- КОНФІГУРАЦІЯ ---
TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('MAXELPAY_API_KEY')
ADMIN_ID = 7749452087
# ВАЖЛИВО: Замініть my-telegram-bot-zqlr на ваш реальний ID проєкту на Render
WEBHOOK_URL = f"https://my-telegram-bot-zqlr.onrender.com"

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
        "1. Select your service: Hyundai VIN to PIN (2017-2026).\n"
        "2. Complete the secure cryptocurrency payment via MaxelPay.\n"
        "3. Provide your VIN number for processing.\n"
        "4. Receive your access PIN-code instantly (15-60 min).\n\n"
        "Press /pay to start your order."
    )

@dp.message(Command("pay"))
async def pay_handler(message: types.Message, state: FSMContext):
    order_id = f"ORDER-{message.from_user.id}"
    link = await create_maxelpay_session(order_id, 200.00) 
    
    if link:
        await message.answer(
            f"Please complete your payment here:\n{link}\n\n"
            "After payment, click the button below:",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="I have paid", callback_data="check_payment")]
            ])
        )
        await state.set_state(Order.waiting_for_payment)
    else:
        await message.answer("Error creating payment session. Please try again later.")

@dp.callback_query(F.data == "check_payment")
async def check_payment(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Payment confirmed! Now please enter your VIN number.")
    await state.set_state(Order.waiting_for_vin)

@dp.message(Order.waiting_for_vin)
async def get_vin(message: types.Message, state: FSMContext):
    vin = message.text
    await bot.send_message(
        ADMIN_ID, 
        f"New order from {message.from_user.id} (@{message.from_user.username or 'No username'}).\nVIN: {vin}"
    )
    await message.answer("VIN received! Processing... Please wait for your PIN-code.")
    await state.clear()

@dp.message(Command("reply"))
async def reply_to_client(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        args = message.text.split()
        if len(args) < 3:
            await message.answer("Usage: /reply [client_id] [pin]")
            return
        client_id, pin = args[1], args[2]
        try:
            await bot.send_message(client_id, f"Your PIN-code is: {pin}")
            await message.answer(f"PIN sent to {client_id} successfully.")
        except Exception as e:
            await message.answer(f"Error: {e}")

async def create_maxelpay_session(order_id, amount):
    url = "https://api.maxelpay.com/api/v1/payments/sessions"
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    payload = {"orderId": order_id, "amount": float(amount), "currency": "USD", "description": "VIN to PIN"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()
                return data.get('data', {}).get('paymentUrl')
    except Exception:
        return None

# --- WEBHOOK ЛОГІКА ---
async def handle_webhook(request):
    update = await request.json()
    await dp.feed_update(bot, types.Update(**update))
    return web.Response(status=200)

async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

if __name__ == "__main__":
    app = web.Application()
    app.router.add_post(f"/{TOKEN}", handle_webhook)
    asyncio.run(on_startup())
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
