from __future__ import annotations
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from ..states import AdminStates
from ..keyboards import kb_formats
from persistence import repositories as repo
from services.report import render_report
from bot.cbdata import pack, unpack

router = Router(name="admin")

def _ik(rows: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)

async def show_admin_menu(m: Message):
    kb = _ik([
        [InlineKeyboardButton(text="Посмотреть список соревнований", callback_data=pack("adm_list", "x"))],
        [InlineKeyboardButton(text="Предложенные соревнования", callback_data=pack("adm_sugs", "x"))],
        [InlineKeyboardButton(text="Добавить соревнование", callback_data=pack("adm_add", "x"))],
    ])
    await m.answer("<b>Админ-меню</b>", reply_markup=kb)

@router.callback_query(F.data.startswith("adm_list"))
async def admin_list_comps(cq: CallbackQuery):
    comps = repo.competitions_list()
    if not comps:
        return await cq.message.edit_text("Соревнований нет.")
    text = "<b>Соревнования</b>\n" + "\n".join(
        f"{i}. {c['title']} — {c['dates_text']} ({c['format']})"
        for i, c in enumerate(comps, 1)
    ) + "\n\nОтправьте номер для просмотра."
    await cq.message.edit_text(text)
    # Запомним список в message id -> не храним глобально; проще попросить номер в чате:
    await cq.answer()

@router.message(F.text.regexp(r"^\d+$"))
async def admin_pick_comp(m: Message, state: FSMContext):
    # Этот хендлер зацепит и участника; защитим текстом:
    # Попадём сюда чаще всего сразу после "Посмотреть список соревнований".
    # Найдём по индексу.
    # Чтобы не смешивать с участником — проверим наличие «админского контекста»: просто пытаемся построить список.
    comps = repo.competitions_list()
    if not comps:
        return
    idx = int(m.text) - 1
    if idx < 0 or idx >= len(comps):
        return
    comp = comps[idx]
    # Покажем все команды по данному comp
    teams = repo.teams_by_competition(comp["id"])
    lines = [f"<b>{comp['title']}</b>\nДаты: {comp['dates_text']} ({comp['format']})"]
    if not teams:
        lines.append("\nЗаявленных команд нет.")
    else:
        for t in teams:
            members = repo.members_by_team(t["id"])
            res = repo.result_for_team(t["id"])
            flag = "" if res else " — <i>Не сдали рапорт</i>"
            members_txt = "\n".join([f"{m['ordinal']}. {m['rank']} {m['fio']} ({m['study_group']} уч. гр.)" for m in members])
            kb = _ik([[InlineKeyboardButton(text="Удалить из списка", callback_data=pack("del_team", t["id"]))]])
            await m.answer(
                f"<b>Команда:</b> {t['name']}{flag}\n"
                f"<b>Капитан:</b> {t['captain_index']}\n"
                f"<b>Место:</b> {t['location']}\n"
                f"<b>Куратор:</b> {t['curator']}\n"
                f"{members_txt}",
                reply_markup=kb
            )
    bottom_kb = _ik([
        [InlineKeyboardButton(text="Сгенерировать рапорт", callback_data=pack("gen_report", comp["id"]))],
        [InlineKeyboardButton(text="Удалить соревнование из списка", callback_data=pack("del_comp", comp["id"]))],
        [InlineKeyboardButton(text="Посмотреть результаты", callback_data=pack("show_res", comp["id"]))],
    ])
    await m.answer("Действия:", reply_markup=bottom_kb)

@router.callback_query(F.data.startswith("del_team"))
async def del_team(cq: CallbackQuery):
    _, v = unpack(cq.data)
    team_id = int(v)
    repo.team_delete(team_id)
    await cq.answer("Команда удалена.")
    await cq.message.edit_text("Команда удалена из списка.")

@router.callback_query(F.data.startswith("del_comp"))
async def del_comp(cq: CallbackQuery):
    _, v = unpack(cq.data)
    comp_id = int(v)
    repo.competition_delete(comp_id)
    await cq.answer("Соревнование удалено.")
    await cq.message.edit_text("Соревнование удалено.")

@router.callback_query(F.data.startswith("show_res"))
async def show_results(cq: CallbackQuery):
    _, v = unpack(cq.data)
    comp_id = int(v)
    rs = repo.results_by_competition(comp_id)
    if not rs:
        return await cq.message.edit_text("Результатов нет.")
    await cq.message.edit_text("<b>Результаты:</b>")
    for r in rs:
        await cq.message.answer(
            f"<b>{r['team_name']}</b>\n"
            f"Место: {r['place']}\n"
            f"Презентация: {(os.path.basename(r['presentation_path']) if r['presentation_path'] else '-')}\n"
            f"Репозиторий: {r['repo_url'] or '-'}\n"
            f"Комментарий: {r['comment'] or '-'}\n"
            f"Сдано: {r['submitted_at']}"
        )
    await cq.answer()

@router.callback_query(F.data.startswith("gen_report"))
async def gen_report(cq: CallbackQuery):
    _, v = unpack(cq.data)
    comp_id = int(v)
    try:
        path = render_report(comp_id)
    except FileNotFoundError as e:
        return await cq.message.answer(str(e))
    await cq.message.answer_document(document=open(path, "rb"), caption="Готовый рапорт")
    await cq.answer()

# ---------- Добавление соревнования админом ----------
@router.callback_query(F.data.startswith("adm_add"))
async def adm_add_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_title)
    await cq.message.edit_text("Название соревнования:")
    await cq.answer()

@router.message(AdminStates.add_title)
async def a_add_title(m: Message, state: FSMContext):
    await state.update_data(title=(m.text or "").strip())
    await state.set_state(AdminStates.add_sponsor)
    await m.answer("Спонсор/Организатор:")

@router.message(AdminStates.add_sponsor)
async def a_add_sponsor(m: Message, state: FSMContext):
    await state.update_data(sponsor=(m.text or "").strip())
    await state.set_state(AdminStates.add_dates)
    await m.answer('Даты проведения. Пример: "29 марта, 30 марта"')

@router.message(AdminStates.add_dates)
async def a_add_dates(m: Message, state: FSMContext):
    await state.update_data(dates=(m.text or "").strip())
    await state.set_state(AdminStates.add_format)
    await m.answer("Формат:", reply_markup=kb_formats())

@router.message(AdminStates.add_format)
async def a_add_format(m: Message, state: FSMContext):
    await state.update_data(fmt=(m.text or "").strip())
    await state.set_state(AdminStates.add_link)
    await m.answer("Ссылка (опционально):")

@router.message(AdminStates.add_link)
async def a_add_link(m: Message, state: FSMContext):
    data = await state.get_data()
    comp_id = repo.competition_add(
        title=data["title"],
        sponsor=data["sponsor"],
        dates_text=data["dates"],
        fmt=data["fmt"],
        link=(m.text or "").strip() or None,
        description="",
        end_date=None  # можно проставлять парсингом, если захотите
    )
    await m.answer(f"Соревнование добавлено (id={comp_id}).")
    await state.clear()

# ---------- Предложенные соревнования ----------
@router.callback_query(F.data.startswith("adm_sugs"))
async def adm_sugs(cq: CallbackQuery):
    pend = repo.suggestions_list("pending")
    if not pend:
        return await cq.message.edit_text("Предложений нет.")
    await cq.message.edit_text("<b>Предложенные соревнования</b>")
    for s in pend:
        kb = _ik([
            [
                InlineKeyboardButton(text="Принять", callback_data=pack("sug_ok", s["id"])),
                InlineKeyboardButton(text="Отклонить", callback_data=pack("sug_no", s["id"])),
            ]
        ])
        await cq.message.answer(
            f"<b>{s['title']}</b>\nОрганизатор: {s['sponsor']}\nДаты: {s['dates_text']}\nФормат: {s['format']}\nСсылка: {s['link'] or '-'}",
            reply_markup=kb
        )
    await cq.answer()

@router.callback_query(F.data.startswith("sug_ok"))
async def sug_accept(cq: CallbackQuery):
    _, v = unpack(cq.data)
    s_id = int(v)
    # Получим саму заявку чтобы перенести поля
    suggestions = repo.suggestions_list("pending")
    s = next((x for x in suggestions if x["id"] == s_id), None)
    if not s:
        return await cq.answer("Заявка не найдена", show_alert=True)
    repo.competition_add(
        title=s["title"], sponsor=s["sponsor"], dates_text=s["dates_text"],
        fmt=s["format"], link=s["link"], description="", end_date=None
    )
    repo.suggestion_update_status(s_id, "approved")
    await cq.message.edit_text("Заявка принята и добавлена в список соревнований.")
    await cq.answer()

@router.callback_query(F.data.startswith("sug_no"))
async def sug_reject(cq: CallbackQuery):
    _, v = unpack(cq.data)
    s_id = int(v)
    repo.suggestion_update_status(s_id, "rejected")
    await cq.message.edit_text("Заявка отклонена.")
    await cq.answer()