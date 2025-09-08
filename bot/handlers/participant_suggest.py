from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from ..states import SuggestStates
from ..keyboards import kb_formats
from persistence import repositories as repo

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
    await m.answer('Даты проведения соревнования. Пример: "29 марта, 30 марта"')

@router.message(SuggestStates.dates)
async def sug_dates(m: Message, state: FSMContext):
    await state.update_data(dates=(m.text or "").strip())
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
    repo.suggestion_add(
        user_id=m.from_user.id,
        title=data["title"],
        sponsor=data["sponsor"],
        dates_text=data["dates"],
        fmt=data["fmt"],
        link=(m.text or "").strip()
    )
    await m.answer("Спасибо! Ваше предложение отправлено админу на рассмотрение.")
    await state.clear()