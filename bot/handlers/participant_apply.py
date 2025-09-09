from __future__ import annotations
from typing import Any
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from ..states import ApplyStates
from ..validators import valid_fio, valid_group
from ..keyboards import kb_ranks, kb_menu, kb_numbers, kb_curators, CURATORS
from persistence import repositories as repo
from config import settings

router = Router(name="participant_apply")

async def start_apply_flow_entry(m: Message, state: FSMContext):
    # 1) вывести список соревнований
    comps = repo.competitions_list()
    if not comps:
        return await m.answer("Активных соревнований пока нет.")
    text = "<b>Доступные соревнования</b>\n" + "\n".join(
        f"{i}. {c['title']} — {c['dates_text']} ({c['format']})" for i, c in enumerate(comps, 1)
    ) + "\n\nОтправьте цифру нужного соревнования."
    await state.set_state(ApplyStates.choosing_comp)
    await state.update_data(_comps=[dict(c) for c in comps])
    await m.answer(text)

@router.message(ApplyStates.choosing_comp, F.text.regexp(r"^\d+$"))
async def choose_comp(m: Message, state: FSMContext):
    data = await state.get_data()
    comps: list[dict[str, Any]] = data.get("_comps", [])
    idx = int(m.text) - 1
    if idx < 0 or idx >= len(comps):
        return await m.answer("Неверный номер. Попробуйте снова.")
    comp = comps[idx]
    desc = comp.get("description") or "-"
    await state.update_data(comp_id=comp["id"])
    await m.answer(f"<b>{comp['title']}</b>\nСпонсор: {comp.get('sponsor') or '-'}\n"
                   f"Даты: {comp['dates_text']}\nФормат: {comp['format']}\nСсылка: {comp.get('link') or '-'}\n\n"
                   f"Описание: {desc}")
    await m.answer("Напишите название команды")
    await state.set_state(ApplyStates.team_name)

@router.message(ApplyStates.team_name)
async def team_name(m: Message, state: FSMContext):
    name = (m.text or "").strip()
    if len(name) < 2:
        return await m.answer("Слишком короткое название. Введите снова.")
    await state.update_data(team_name=name)
    await m.answer("Сколько человек в команде? (не более 5)")
    await state.set_state(ApplyStates.team_size)

@router.message(ApplyStates.team_size, F.text.regexp(r"^\d$"))
async def team_size(m: Message, state: FSMContext):
    n = int(m.text)
    if n < 1 or n > 5:
        return await m.answer("Число должно быть от 1 до 5. Введите снова.")
    await state.update_data(team_size=n, member_idx=1, members=[])
    await m.answer("1 участник\nУкажите воинское звание", reply_markup=kb_ranks())
    await state.set_state(ApplyStates.member_rank)

@router.message(ApplyStates.member_rank)
async def member_rank(m: Message, state: FSMContext):
    rank = (m.text or "").strip()
    await state.update_data(current_rank=rank)
    await m.answer('Фамилия и инициалы. Пример: "Иванов И.И."')
    await state.set_state(ApplyStates.member_fio)

@router.message(ApplyStates.member_fio)
async def member_fio(m: Message, state: FSMContext):
    fio = (m.text or "").strip()
    if not valid_fio(fio):
        return await m.answer('Формат неверный. Пример: "Иванов И.И." Повторите ввод.')
    await state.update_data(current_fio=fio)
    await m.answer('Введите номер учебной группы. Пример: 666/66 или 666 (без пробелов)')
    await state.set_state(ApplyStates.member_group)

@router.message(ApplyStates.member_group)
async def member_group(m: Message, state: FSMContext):
    group = (m.text or "").strip()
    if not valid_group(group):
        return await m.answer('Формат группы неверный. Допустимы только цифры и "/". Повторите.')
    data = await state.get_data()
    members = data.get("members", [])
    idx = data.get("member_idx", 1)
    members.append((idx, data["current_rank"], data["current_fio"], group))
    await state.update_data(members=members)

    if idx < data["team_size"]:
        next_idx = idx + 1
        await state.update_data(member_idx=next_idx)
        await m.answer(f"{next_idx} участник\nУкажите воинское звание", reply_markup=kb_ranks())
        await state.set_state(ApplyStates.member_rank)
    else:
        await m.answer("Укажите номер капитана команды", reply_markup=kb_numbers(data["team_size"]))
        await state.set_state(ApplyStates.captain)

@router.message(ApplyStates.captain, F.text.regexp(r"^\d$"))
async def captain_pick(m: Message, state: FSMContext):
    data = await state.get_data()
    cap = int(m.text)
    if cap < 1 or cap > data["team_size"]:
        return await m.answer("Неверный номер. Повторите.")
    await state.update_data(captain_index=cap)
    await m.answer('Укажите место проведения. Пример: "г. Санкт-Петербург, наб. Карповки 5АК"')
    await state.set_state(ApplyStates.location)

@router.message(ApplyStates.location)
async def location_set(m: Message, state: FSMContext):
    loc = (m.text or "").strip()
    if "," not in loc or not loc.lower().startswith(("г.", "город")):
        return await m.answer('Формат адреса: "г. <Город>, <полный адрес>". Повторите.')
    await state.update_data(location=loc)
    await m.answer("Выберите куратора", reply_markup=kb_curators())
    await state.set_state(ApplyStates.curator)

@router.message(ApplyStates.curator)
async def curator_set(m: Message, state: FSMContext):
    curator = (m.text or "").strip()
    data = await state.get_data()
    comp_id = data["comp_id"]
    team_id = repo.team_add(
        competition_id=comp_id,
        name=data["team_name"],
        member_count=data["team_size"],
        captain_index=data["captain_index"],
        location=data["location"],
        curator=curator,
        user_id=m.from_user.id
    )
    repo.members_add_bulk(team_id, data["members"])
    is_admin = m.from_user.id in settings.ADMIN_IDS
    # (опционально) вытащим название соревнования, если есть такой репозиторийный метод
    comp_title = ""
    try:
        comp = repo.competition_get(comp_id)  # если такого метода нет — убери этот блок
        comp_title = comp["title"]
    except Exception:
        pass

    await state.clear()
    await m.answer(
        "Заявка принята ✅\n"
        + (f"Соревнование: {comp_title}\n" if comp_title else "")
        + f"Команда: {data['team_name']}\n"
          f"Участников: {data['team_size']}\n"
          f"Куратор: {curator}\n"
          f"Место: {data['location']}",
        reply_markup=kb_menu(is_admin=is_admin)
    )
    # Итоговый список команды
    members_txt = "\n".join([f"{o}. {r} {f} ({g} уч. гр.)" for o, r, f, g in data["members"]])
    await m.answer(
        "<b>Заявка принята!</b>\n\n"
        f"<b>Команда:</b> {data['team_name']}\n"
        f"<b>Капитан:</b> {data['captain_index']}\n"
        f"<b>Место:</b> {data['location']}\n"
        f"<b>Куратор:</b> {curator}\n\n"
        f"{members_txt}"
    )
    await state.clear()