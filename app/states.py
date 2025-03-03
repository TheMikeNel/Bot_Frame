from aiogram.fsm.state import State, StatesGroup

class UserState(StatesGroup):
    msg_ids = State()

class Authorization(UserState):
    authorized = State()
    cart = State()

class Job(Authorization):
    select_job = State()

class Administrating(Job):
    select_admin = State()
    add_user_id = State()
    add_user_name = State()
    add_user_role = State()
    delete_id = State()