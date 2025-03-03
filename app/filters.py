from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from .states import UserState

class NotAuthFilter(Filter):
    async def __call__(self, state: FSMContext) -> bool:
        curr: str = await state.get_state()
        return (curr == None or curr == UserState.msg_ids)
    
class AuthFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        curr: str = await state.get_state()
        return (curr != None and curr != UserState.msg_ids)

class AuthRoleFilter(Filter):
    def __init__(self, *required_roles):
        self.required_roles = required_roles

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        if 'authorized' in data:
            auth_user = data['authorized']
            user_role = auth_user[1]
            for role in self.required_roles:
                if user_role == role: return True
        return False