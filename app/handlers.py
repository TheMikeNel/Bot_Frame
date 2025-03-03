import logging
from . import base, kboards as kb, filters as f, states as st
from database import db

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.photo, f.AuthFilter())
async def get_photo(message: Message, state: FSMContext):
    pass    

@router.message(st.Administrating.add_user_id)
async def get_auth_name(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(add_user_id=message.text)
        await base.send_answer("Теперь введите имя пользователя.", message, state)
        await state.set_state(st.Administrating.add_user_name)
    else: await base.send_answer("Некорректный ID. Повторите ввод.", message, state)

@router.message(st.Administrating.add_user_name)
async def get_auth_role(message: Message, state: FSMContext):
    await state.update_data(add_user_name=message.text)
    await base.send_answer("Выберите роль для пользователя: admin или worker.", message, state, reply_markup=kb.user_roles())
    await state.set_state(st.Administrating.add_user_role)

@router.message(st.Administrating.add_user_role)
async def create_new_user(message: Message, state: FSMContext):
    if message.text == 'worker' or message.text == 'admin':
        await state.update_data(add_user_role=message.text)
        data = await state.get_data()
        id = data['add_user_id']
        name = data['add_user_name']
        role = data['add_user_role']
        if db.user_operator.add_user(id, name, role):
            await base.send_answer(f"Пользователь \"{name}\" создан!", message, state)
        else: 
            await base.send_sticker("CAACAgIAAxkBAAENnnNnkiaJ58IjJ1D6dX9i71_vf7-RIgACGQAD8_KOPwSqpI7gxjzLNgQ", message, state)
        await state.set_state(st.Authorization.authorized)
    else:
        await base.send_answer("Выбрана некорректная роль. Выберите admin или worker.", message, state)

@router.message(st.Administrating.delete_id)
async def delete_user(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(delete_id=message.text)
        if db.user_operator.delete_users(message.text):
            await base.send_answer("Пользователь успешно удалён.", message, state)
        else:
            await base.send_answer("Пользователь с указанным ID не найден.", message, state)
        await state.set_state(st.Authorization.authorized)
    else: await base.send_answer("Некорректный ID. Повторите ввод.", message, state)

@router.message(StateFilter(None))
@router.message(StateFilter(f.UserState))
async def get_nauth_message(message: Message, state: FSMContext):
    user_msg = f"User ID: {message.from_user.id}, with name {message.from_user.full_name} and username {message.from_user.username} sends the message: {message.text}"
    logging.warning(user_msg)
    await base.send_answer(f"Пройди авторизацию (/start).\nА если хочешь пообщаться то я могу тебе ответить тем же:\n{message.text}", message, state, reply_markup=kb.start())

@router.message(st.Authorization.authorized, F.text)
async def get_auth_message(message: Message, state: FSMContext):
    await base.send_answer(f"Свои, свои: {message.text}", message, state)
