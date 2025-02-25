from aiogram.fsm.state import State, StatesGroup


class AddEstateState(StatesGroup):
    phone = State()
    description = State()
    photos = State()
    barter_to = State()
