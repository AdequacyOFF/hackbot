from __future__ import annotations
import os
from typing import Any
from aiogram import Router, F
from aiogram.types import Message, ContentType, Document
from aiogram.fsm.context import FSMContext
from ..states import ResultsStates
from persistence import repositories as repo
from config import settings
from datetime import datetime, timedelta
import re

router = Router(name="participant_results")

def _parse_end_date(dates_text: str) -> datetime | None:
    # Пытаемся вытащить последнюю дату из "29 марта, 30 марта" и добавить текущий/следующий год разумно.
    months = {
        "января":1,"февраля":2,"марта":3,"апреля":4,"мая":5,"июня":6,
        "июля":7,"августа":8,"сентября":9,"октября":10,"ноября":11,"декабря":12
    }
    parts = [p.strip() for p in re.split(r"[,\s]+и\s+|,|\s+и\s+", dates_text) if p.strip()]
    # берем последнюю полноценную "DD <месяца> [YYYY]"
    last = parts[-1] if parts else ""
    m = re.match(r"^(\d{1,2})\s+([А-Яа-яёЁ]+)(?:\s+(\d{4}))?$", last)
    if not m:
        return None
    day = int(m.group(1))
    mon = months.get(m.group(2).lower())
    if not mon:
        return None
    year = int(m.group(3)) if m.group(3) else datetime.now(settings.TZ).year
    try:
        return datetime(year, mon, day, tzinfo=settings.TZ)
    except Exception:
        return None

async def start_results_flow_entry(m: Message, state: FSMContext):
    # Выводим список команд пользователя по всем соревнованиям (или все команды, где user_id = текущий)
    # Если хотите — можно выводить сперва соревнование, но по ТЗ: список названий команд.
    # Для простоты — пройдёмся по всем активным соревнованиям и соберём команды пользователя.
    comps = repo.competitions_list()
    items: list[tuple[int, int, str]] = []  # (idx, team_id, display)
    idx = 1
    for c in comps:
        teams = repo.teams_by_competition(c["id"])
        for t in teams:
            if t["user_id"] == m.from_user.id:
                items.append((idx, t["id"], f"{idx}. {t['name']} — {c['title']}"))
                idx += 1
    if not items:
        return await m.answer("У вас нет команд для подачи результатов.")
    await state.set_state(ResultsStates.picking_team)
    await state.update_data(_list=items)
    txt = "<b>Ваши команды</b>\n" + "\n".join([it[2] for it in items]) + "\n\nОтправьте номер вашей команды."
    await m.answer(txt)

@router.message(ResultsStates.picking_team, F.text.regexp(r"^\d+$"))
async def pick_team(m: Message, state: FSMContext):
    data = await state.get_data()
    L: list[tuple[int, int, str]] = data.get("_list", [])
    num = int(m.text)
    pick = next((x for x in L if x[0] == num), None)
    if not pick:
        return await m.answer("Неверный номер. Повторите.")
    team_id = pick[1]
    team = repo.team_get(team_id)
    comp = repo.competition_get(team["competition_id"])
    # Дедлайн: до 00:00 (end_date + 1 день)
    if comp and comp["end_date"]:
        try:
            deadline = datetime.fromisoformat(comp["end_date"])
        except Exception:
            deadline = _parse_end_date(comp["dates_text"]) or datetime.now(settings.TZ)
    else:
        deadline = _parse_end_date(comp["dates_text"]) if comp else None

    if deadline:
        deadline_dt = datetime(deadline.year, deadline.month, deadline.day, 0, 0, tzinfo=settings.TZ) + timedelta(days=1)
        now = datetime.now(settings.TZ)
        if now > deadline_dt:
            await m.answer(f"Срок сдачи результатов истёк (до 00:00 {deadline_dt.strftime('%d.%m.%Y')}). "
                           f"Отправка будет отмечена как просроченная.")
            await state.update_data(late=True)
    await state.update_data(team_id=team_id, comp_id=team["competition_id"])
    await m.answer("Занятое место (цифрой)")
    await state.set_state(ResultsStates.place)

@router.message(ResultsStates.place, F.text.regexp(r"^\d+$"))
async def set_place(m: Message, state: FSMContext):
    await state.update_data(place=int(m.text))
    await m.answer("Прикрепите файл с презентацией (PDF или PPTX)")
    await state.set_state(ResultsStates.presentation)

@router.message(ResultsStates.presentation, F.document)
async def take_presentation(m: Message, state: FSMContext):
    doc: Document = m.document
    fn = (doc.file_name or "").lower()
    if not (fn.endswith(".pdf") or fn.endswith(".pptx") or fn.endswith(".ppt")):
        return await m.answer("Нужен файл PDF/PPT/PPTX.")
    # сохраняем
    file = await m.bot.get_file(doc.file_id)
    dest = os.path.join(settings.FILES_DIR, f"{doc.file_id}_{doc.file_unique_id}_{doc.file_name}")
    await m.bot.download_file(file.file_path, destination=dest)
    await state.update_data(presentation_path=dest)
    await m.answer("Укажите ссылку на репозиторий (http/https).")
    await state.set_state(ResultsStates.repo)

@router.message(ResultsStates.repo, F.text.startswith(("http://", "https://")))
async def set_repo(m: Message, state: FSMContext):
    await state.update_data(repo_url=m.text.strip())
    await m.answer("Комментарий к результатам (в свободной форме)")
    await state.set_state(ResultsStates.comment)

@router.message(ResultsStates.repo)
async def bad_repo(m: Message, state: FSMContext):
    await m.answer("Ссылка должна начинаться с http:// или https://. Повторите.")

@router.message(ResultsStates.comment)
async def set_comment(m: Message, state: FSMContext):
    data = await state.get_data()
    repo.result_add(
        competition_id=data["comp_id"],
        team_id=data["team_id"],
        place=data["place"],
        presentation_path=data.get("presentation_path"),
        repo_url=data.get("repo_url"),
        comment=m.text or ""
    )
    await m.answer("Результаты приняты. Спасибо!")
    await state.clear()