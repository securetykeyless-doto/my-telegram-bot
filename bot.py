import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Стани для діалогу
class OrderStates(StatesGroup):
    waiting_for_payment = State()
    waiting_for_contact = State()
    waiting_for_address = State()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привіт! Натисни /pay, щоб отримати посилання на оплату.")

@dp.message(Command("pay"))
async def pay_handler(message: types.Message, state: FSMContext):
    # Тут ви будете викликати API MaxelPay для генерації посилання
    payment_url = "https://maxelpay.example.com/pay/12345" # Приклад
    await message.answer(f"Ось ваше посилання на оплату: {payment_url}\nПісля оплати напишіть свій номер телефону.")
    await state.set_state(OrderStates.waiting_for_contact)

@dp.message(OrderStates.waiting_for_contact)
async def get_contact(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Дякую! Тепер напишіть вашу адресу доставки.")
    await state.set_state(OrderStates.waiting_for_address)

@dp.message(OrderStates.waiting_for_address)
async def get_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    phone = data['phone']
    address = message.text
    await message.answer(f"Замовлення прийнято!\nТелефон: {phone}\nАдреса: {address}\nМи скоро зв'яжемося!")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
