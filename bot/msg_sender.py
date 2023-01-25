import logging

import aioschedule
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from werkzeug.security import check_password_hash

from main import db, TOKEN
from models import User, Message, BotAuth
from utils import Login

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Its bot for getting notification.\n'
                         '/login - to log in')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('canceled', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['login'])
async def login(message: types.Message):
    await Login.email.set()
    await message.answer('write your email')


@dp.message_handler(state=Login.email)
async def get_email(message: types.Message, state: FSMContext):
    email = message.text
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        await state.update_data(email=email, user_id=user.id, pwd=user.password)
        await Login.password.set()
        await message.answer('write your password')
    else:
        await message.answer('wrong email. Sign up on the site or write another email')
        await Login.email.set()


@dp.message_handler(state=Login.password)
async def get_password(message: types.Message, state: FSMContext):
    password = message.text
    async with state.proxy() as d:
        user_id = d['user_id']
        pwd = d['pwd']
    if check_password_hash(pwd, password):
        auth_user = BotAuth(user_id=user_id, chat_id=message.chat.id)
        db.session.add(auth_user)
        db.session.commit()
        await state.finish()
        await message.answer('login successfully completed')


async def send_new_messages():
    auth_users = db.session.query(BotAuth).all()
    for user in auth_users:
        messages = db.session.query(Message).filter_by(user_id=user.id, sent=False).all()
        str_msgs = '\n'.join(messages)
        await bot.send_message(user.chat_id, str_msgs)


async def scheduler():
    aioschedule.every().day.at('12:00').do(send_new_messages)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
