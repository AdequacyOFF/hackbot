from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

RANKS = ["ст.сержант", "сержант", "мл.сержант", "рядовой"]
CURATORS = ["ДАС и ТПВ", "ХТА"]
FORMAT_CHOICES = ["онлайн", "офлайн"]
BACK_BUTTON_TEXT = "⬅️ В меню"

def kb_menu(is_admin: bool) -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.add(KeyboardButton(text="Подать заявку"))
    b.add(KeyboardButton(text="Результаты участия"))
    b.add(KeyboardButton(text="Предложить соревнование"))
    if is_admin:
        b.row(KeyboardButton(text="Админ-меню"))
    b.row(KeyboardButton(text=BACK_BUTTON_TEXT))
    return b.as_markup(resize_keyboard=True)

def kb_ranks() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    for r in RANKS: b.add(KeyboardButton(text=r))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)

def kb_curators() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    for c in CURATORS: b.add(KeyboardButton(text=c))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)

def kb_formats() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    for f in FORMAT_CHOICES: b.add(KeyboardButton(text=f))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)

def kb_numbers(n: int) -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    for i in range(1, n+1): b.add(KeyboardButton(text=str(i)))
    return b.as_markup(resize_keyboard=True, one_time_keyboard=True)