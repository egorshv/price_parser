from aiogram.dispatcher.filters.state import State, StatesGroup


class Login(StatesGroup):
    email = State()
    password = State()
