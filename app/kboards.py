from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from services.getconf import Commands

def start() -> ReplyKeyboardMarkup: return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/start')]], resize_keyboard=True)

def to_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Вернуться в меню", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Изменить данные", callback_data="set_data")
    return builder.as_markup(resize_keyboard=True)

def admins():
    builder = InlineKeyboardBuilder()
    builder.button(text="👨🏻‍🔧Добавить пользователя", callback_data='admin_add_usr')
    builder.button(text="⛔Удалить пользователя", callback_data="admin_delete_usr")
    builder.button(text="🧾Все пользователи", callback_data="admin_show_usrs")
    builder.button(text="🏠В меню", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def user_roles():
    builder = ReplyKeyboardBuilder()
    builder.button(text='worker')
    builder.button(text='admin')
    builder.button(text=f'{emoji.emojize(Commands.menu)} в меню') #menu
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)