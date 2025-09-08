from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import settings
from .participant_apply import start_apply_flow_entry
from .participant_results import start_results_flow_entry
from .participant_suggest import start_suggest_flow_entry
from ..keyboards import kb_menu

router = Router(name="common")

RULES_TEXT = (
    "<b>Правила бота</b>\n"
    "• Подайте заявку на участие команды в хакатоне.\n"
    "• После завершения — загрузите результат (место, презентацию, репозиторий, комментарий).\n"
    "• Вы можете предложить своё соревнование.\n"
    "• Администратор видит все заявки и может сгенерировать рапорт.\n\n"
    "Нажмите нужный пункт меню."
)

@router.message(F.text == "/start")
async def cmd_start(m: Message, state: FSMContext):
    is_admin = m.from_user.id in settings.ADMIN_IDS
    await state.clear()
    if is_admin:
        # Как просили: две роли в виде кнопок можно эмулировать кнопкой «Админ-меню» в общем меню.
        await m.answer(RULES_TEXT, reply_markup=kb_menu(is_admin=True))
    else:
        await m.answer(RULES_TEXT, reply_markup=kb_menu(is_admin=False))

@router.message(F.text.lower() == "подать заявку")
async def menu_apply(m: Message, state: FSMContext):
    await start_apply_flow_entry(m, state)

@router.message(F.text.lower() == "результаты участия")
async def menu_results(m: Message, state: FSMContext):
    await start_results_flow_entry(m, state)

@router.message(F.text.lower() == "предложить соревнование")
async def menu_suggest(m: Message, state: FSMContext):
    await start_suggest_flow_entry(m, state)

# Вход в админ-меню
@router.message(F.text.lower() == "админ-меню")
async def admin_entry(m: Message):
    from .admin import show_admin_menu
    if m.from_user.id not in settings.ADMIN_IDS:
        return await m.answer("Доступ запрещён.")
    await show_admin_menu(m)