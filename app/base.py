import logging

from . import kboards
from . import states as st
from services.getconf import Stickers
from database import db

from aiogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardMarkup, InputMedia
from aiogram.fsm.context import FSMContext

async def fetch_msgs(messages: list[Message], state: FSMContext):
    if await state.get_state() == None:
        await state.set_state(st.UserState.msg_ids)

    data = await state.get_data()
    curr = list()
    if 'msg_ids' in data and data['msg_ids'] != None and len(data['msg_ids']) > 0:
        curr.extend(data['msg_ids'])
    
    to_fetch: list[int] = list()
    for msg in messages:
        to_fetch.append(msg.message_id)

    curr.extend(to_fetch)
    result = list(set(curr))
    result.sort()

    print(f"Fetch {to_fetch} to current {curr}. result: {result}")
    await state.update_data(msg_ids=result)

async def set_temp_message(message: Message, state: FSMContext):
    await state.update_data(temp_msg=message.message_id)

async def delete_temp_message(message: Message, state: FSMContext):
    data = await state.get_data()
    if 'temp_msg' in data and data['temp_msg'] != None:
        await delete_message(message, state, data['temp_msg'])

async def delete_previous_message(message: Message, state: FSMContext, steps_to_back: int = 1):
    msg_id = message.message_id
    required_id = msg_id - steps_to_back
    chat = message.from_user.id
    data = await state.get_data()
    if 'msg_ids' in data:
        ids = data['msg_ids']
        if type(ids) is list:
            if msg_id in ids:
                i = ids.index(msg_id) - steps_to_back
                if i >= 0:
                    required_id = ids[i]
            else:
                i = len(ids) - 1 - steps_to_back
                if i >= 0:
                    required_id = ids[i]
            ids.remove(required_id)
            await state.update_data(msg_ids=ids)
    try: message.bot.delete_message(chat, required_id)
    except: logging.warning(f"Message not found to delete: {msg_id}")

async def delete_message(message: Message, state: FSMContext, other_id: int | None = None):
    data = await state.get_data()
    msg_id = message.message_id
    if other_id != None:
        msg_id = other_id
        try: await message.bot.delete_message(message.from_user.id, msg_id)
        except: logging.warning(f"Message not found to delete: {msg_id}")
    else:
        try: await message.delete()
        except: logging.warning(f"Message not found to delete: {message.message_id}")

    if 'msg_ids' in data and data['msg_ids'] != None and len(data['msg_ids']) > 0:
        msgs = list(data['msg_ids'])
        if msg_id in msgs: msgs.remove(msg_id)
        await state.update_data(msg_ids=msgs)
    else: print(f"Havent msg '{msg_id}' in data: {data}")

async def clear_messages(message: Message, state: FSMContext, end_text: str = "Чат теперь чист!", with_exit = False):
    if await state.get_state() == None: return
    data = await state.get_data()
    if 'msg_ids' in data and data['msg_ids'] != None and len(data['msg_ids']) > 0:
        ids = data['msg_ids']
        print(f"Messages to delete: {ids}")
        #if len(ids) > 99:
        for id in ids: 
            try: await message.bot.delete_message(message.from_user.id, id)
            except BaseException: logging.warning(f"Message not found to delete: {id}")
        #else: await message.bot.delete_messages(message.from_user.id, ids)
        await state.update_data(msg_ids=None)
    else: print("No data to delete")
    if not with_exit and 'authorized' in data and data['authorized'] != None:
        user = data['authorized']
        await state.clear()
        await state.set_state(st.Authorization.authorized)
        await state.update_data(authorized=user)
        await menu(message, state)
    else:
        await state.clear()
        await send_answer(end_text, message, state, reply_markup=kboards.start())

async def exit(message: Message, state: FSMContext):
    await clear_messages(message, state, "Вы вышли из системы.", True)

async def send_answer(text: str, message: Message, state: FSMContext, delete_prev_msg = True, to_main_keyboard = True, *, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None):
    try: await message.delete_reply_markup()
    except: logging.warning(f"Message {message.message_id} can't be edited.")

    if to_main_keyboard and reply_markup == None:
        msg = await message.answer(text, reply_markup=kboards.to_menu())
    else: msg = await message.answer(text, reply_markup=reply_markup)
    if delete_prev_msg:
        await delete_temp_message(message, state)
        await set_temp_message(msg, state)
        await delete_message(message, state)
        await fetch_msgs([msg], state)
    else: await fetch_msgs([message, msg], state)

async def send_sticker(id: str, message: Message, state: FSMContext, delete_prev_msg: bool = True, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None):
    try: await message.delete_reply_markup()
    except: logging.warning(f"Message {message.message_id} can't be edited.")

    msg = await message.answer_sticker(id, reply_markup=reply_markup)
    if delete_prev_msg:
        await delete_temp_message(message, state)
        await set_temp_message(msg, state)
        await delete_message(message, state)
        await fetch_msgs([msg], state)
    else: await fetch_msgs([message, msg], state)

async def send_media(media: list[InputMedia], message: Message, state: FSMContext, delete_prev_msg = True):
    try: await message.delete_reply_markup()
    except: logging.warning(f"Message {message.message_id} can't be edited.")

    msg = await message.answer_media_group(media)
    if delete_prev_msg:
        await delete_temp_message(message, state)
        await set_temp_message(msg, state)
        await delete_message(message, state)
        await fetch_msgs([msg], state)
    else: await fetch_msgs([message, msg], state)

async def menu(message: Message, state: FSMContext):
    if await state.get_state() != None: await state.set_state(st.Authorization.authorized)
    role = await get_current_role(state)
    await send_sticker(Stickers.jobs, message, state, reply_markup=kboards.menu(role))

async def autorize_user(message: Message, state: FSMContext) -> bool:
    user = db.user_operator.authorize(message.from_user.id)
    if user != None:
        await state.update_data(authorized=user.to_dict())
        await state.set_state(st.Authorization.authorized)
        await message.answer("✌︎︎", reply_markup=kboards.main())
        await send_answer(f"✅Авторизация пройдена✅\n{user}", message, state, to_main_keyboard=False)
        return True 
    else:
        await send_answer(f"❌Авторизация не пройдена❌\nДля авторизации обратитесь к администратору, переслав ему следующие данные:\n\nUser ID: {message.from_user.id}\nName: {message.from_user.full_name}", message, state)
        return False

async def get_current_role(state: FSMContext):
    data = await state.get_data()
    if 'authorized' in data:
        auth_user = data['authorized']
        return auth_user['user_role']