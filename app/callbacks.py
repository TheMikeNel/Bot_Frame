from . import base, kboards as kb, states as st, filters as f
from database import db
from services import getconf as conf
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == 'back_to_menu')
async def to_menu(callback: CallbackQuery, state: FSMContext):
    await base.menu(callback.message, state)

@router.callback_query(F.data == 'exit')
async def user_exit(callback: CallbackQuery, state: FSMContext):
    await base.exit(callback.message, state)

@router.callback_query(F.data == 'admin', f.AuthRoleFilter('super', 'admin'))
async def admin(callback: CallbackQuery, state: FSMContext):
    await state.set_state(st.Administrating.select_admin)
    await base.send_sticker(conf.Stickers.admin, callback.message, state, reply_markup=kb.admins())

@router.callback_query(st.Administrating.select_admin) # ADMIN
async def do_admin(callback: CallbackQuery, state: FSMContext):
    msg = callback.message
    text = callback.data
    if text == 'admin_add_usr':
        await base.send_answer("Добавление нового пользователя. Введите ID:", msg, state)
        await state.set_state(st.Administrating.add_user_id)
    elif text == 'admin_delete_usr':
        await base.send_answer("Удаление пользователя. Введите ID:", msg, state)
        await state.set_state(st.Administrating.delete_id)
    elif text == 'admin_show_usrs':
        users = db.user_operator.get_all_users(format=True)
        temp = ""
        for user in users:
            temp += user
        await base.send_answer(f"Список всех пользователей системы:\n{temp}", msg, state)

@router.callback_query(F.data.startswith('set_')) # все операции по изменению данных
async def set_job(callback: CallbackQuery):
    text = callback.data
    
    if text == 'set_status':
        pass