from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config import settings
from .participant_apply import start_apply_flow_entry
from .participant_results import start_results_flow_entry
from .participant_suggest import start_suggest_flow_entry
from ..keyboards import kb_menu, BACK_BUTTON_TEXT

router = Router(name="common")

RULES_TEXT = (
    "<b>АХТУНГ!!!</b>\n"
    "Товарищ хакатонщик! Этот бот создан в качестве поддержки для ваших старших товарищей и лиц из числа командования лучшей кафедры академии!\n"
    "P.S. А также для упрощения жизни приемственных поколений.\n\n"
    "<b><u>Правила бота:</u></b>\n"
    "<i>1. Вы можете подать заявку на участие команды в конкретном соревновании, а также предложить своё соревнование.</i>\n"
    "<i>2. После завершения соревнования обязательно отправьте отчёт за команду: занятое место, презентацию (PDF/PPT/PPTX), ссылку на репозиторий и краткий комментарий.</i>\n"
    "<i>3.Будьте внимательны: соблюдайте орфографию, пунктуацию и формат, следуйте примерам в подсказках бота.</i>\n\n"
    "Эти три правила будут считаться основой для вашей лучшей жизни.\n\n"
    "<b><u>А теперь о последствиях:</u></b>\n"
    "<i>1) При подаче заявки строго следуйте требованиям бота. Неверный формат (ФИО, группы, адреса и т. п.) или неаккуратное оформление могут привести к тому, что команда не попадёт в рапорт. <b>Предупреждён — значит вооружён!</b></i>\n"
    "<i>2) Хотите предложить соревнование — оформляйте его по образцу: корректные даты, формат, организатор и ссылка повышают шансы на рассмотрение.</i>\n"
    "<i>3) Не забывайте об отчете после окончания соревнования. В него должны входить: результаты согласно турнирной таблицы, презентация, ссылка на репозиторий + краткий отзыв. <b>Помни!</b> Отчет нужно подать сразу после оглашения результатов соревнования, в противном случае вы и ваша команда попадете в ""список пидорасов""</i>\n"
    "<i>4) Не заебывайте админа в личке! Вылет из рапорта - это целиком и полностью ваша вина. В 100lv вкаченное красноречие, 10-этажный мат, вызов сатаны и слезы тут не помогут. Ценим время друг друга.</i>\n\n"
    "<b><i><u>Нажмите нужный пункт меню.</u></i></b>"
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
    
@router.message(F.text == BACK_BUTTON_TEXT)
async def go_back_to_menu(m: Message, state: FSMContext):
    # сбрасываем состояние и показываем главное меню
    await state.clear()
    is_admin = m.from_user.id in settings.ADMIN_IDS
    await m.answer("Главное меню:", reply_markup=kb_menu(is_admin=is_admin))