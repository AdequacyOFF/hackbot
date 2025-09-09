from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from ..states import SuggestStates
from ..keyboards import kb_formats
from persistence import repositories as repo
from ..validators import parse_date_range_strict
from services.dates import infer_last_date_iso
from config import settings
from ..keyboards import kb_menu

router = Router(name="participant_suggest")

async def start_suggest_flow_entry(m: Message, state: FSMContext):
    await state.set_state(SuggestStates.title)
    await m.answer("Укажите название соревнования")

@router.message(SuggestStates.title)
async def sug_title(m: Message, state: FSMContext):
    await state.update_data(title=(m.text or "").strip())
    await state.set_state(SuggestStates.sponsor)
    await m.answer('Кем проводится? Пример: "ПАО Сбербанк"')

@router.message(SuggestStates.sponsor)
async def sug_sponsor(m: Message, state: FSMContext):
    await state.update_data(sponsor=(m.text or "").strip())
    await state.set_state(SuggestStates.dates)
    await m.answer(
        'Даты проведения (строго без пробелов): "ДД.ММ.ГГГГ-ДД.ММ.ГГГГ"\n'
        'Пример: 29.05.2025-30.05.2025\n'
        'Значение не принимается, если есть пробелы или формат неверный.'
    )

@router.message(SuggestStates.dates)
async def sug_dates(m: Message, state: FSMContext):
    txt = (m.text or "").strip()
    rng = parse_date_range_strict(txt)
    if not rng:
        return await m.answer(
            'Даты проведения (строго без пробелов): "ДД.ММ.ГГГГ-ДД.ММ.ГГГГ"\n'
            'Пример: 29.05.2025-30.05.2025\n'
            'Значение не принимается, если есть пробелы или формат неверный.'
        )
    await state.update_data(dates=txt)
    await state.set_state(SuggestStates.format)
    await m.answer("Укажите формат", reply_markup=kb_formats())

@router.message(SuggestStates.format)
async def sug_format(m: Message, state: FSMContext):
    await state.update_data(fmt=(m.text or "").strip())
    await state.set_state(SuggestStates.link)
    await m.answer("Ссылка на соревнование")

@router.message(SuggestStates.link)
async def sug_link(m: Message, state: FSMContext):
    data = await state.get_data()
    # сразу сохраним end_date для дедлайна
    end_iso = infer_last_date_iso(data["dates"])
    repo.suggestion_add(
        user_id=m.from_user.id,
        title=data["title"],
        sponsor=data["sponsor"],
        dates_text=data["dates"], 
        fmt=data["fmt"],
        link=(m.text or "").strip()
    )
    is_admin = m.from_user.id in settings.ADMIN_IDS
    await state.clear()
    await m.answer(
        "Спасибо! Ваше предложение отправлено админу на рассмотрение.",
        reply_markup=kb_menu(is_admin=is_admin)
    )