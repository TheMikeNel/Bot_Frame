import emoji

from . import base, kboards as kb, filters as f, states as st
from services.getconf import Commands, Stickers

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command('state'))
async def check_state(message: Message, state: FSMContext):
    await base.send_answer(f"Current state is {await state.get_state()}", message, state, to_main_keyboard=False)

@router.message(Command('data'))
async def state_data(message: Message, state: FSMContext):
    await base.send_answer(f"Current state data: {await state.get_data()}", message, state, to_main_keyboard=False)

@router.message(Command('clear'))
@router.message(F.text == emoji.emojize(Commands.clear))
async def clear_chat(message: Message, state: FSMContext):
    await base.clear_messages(message, state)

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await base.send_answer(
        f"Привет! Я KIP бот от Zero!\nЯ помогу тебе с данными по КИП! (Доступ только авторизованным пользователям).", 
        message, state, to_main_keyboard=False)
    if await f.NotAuthFilter().__call__(state):
        if await base.autorize_user(message, state):
            await base.menu(message, state)
    else: await base.menu(message, state)

@router.message(Command('menu'))
@router.message(F.text == emoji.emojize(Commands.menu), f.AuthFilter())
async def menu(message: Message, state: FSMContext):
    await base.menu(message, state)

@router.message(Command('admin'))
@router.message(F.text == emoji.emojize(Commands.admin), f.AuthRoleFilter('super', 'admin'))
async def admin(message: Message, state: FSMContext):
    await state.set_state(st.Administrating.select_admin)
    await base.send_sticker(Stickers.admin, message, state, reply_markup=kb.admins())