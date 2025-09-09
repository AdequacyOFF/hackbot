from __future__ import annotations
import os
import sqlite3
from contextlib import closing
from docxtpl import DocxTemplate
from config import settings
from services.dates import human_dates_with_times  # важно: берём новую реализацию

def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def build_context(comp_id: int) -> dict:
    with closing(_db()) as conn:
        comp = conn.execute(
            "SELECT * FROM competitions WHERE id=?",
            (comp_id,)
        ).fetchone()
        if comp is None:
            raise ValueError(f"Соревнование id={comp_id} не найдено")

        teams = conn.execute(
            "SELECT * FROM teams WHERE competition_id=? ORDER BY id",
            (comp_id,)
        ).fetchall()

        members_by_team: dict[int, list[sqlite3.Row]] = {}
        for t in teams:
            mems = conn.execute(
                "SELECT * FROM members WHERE team_id=? ORDER BY ordinal",
                (t["id"],)
            ).fetchall()
            members_by_team[t["id"]] = mems

    def team_dict(t: sqlite3.Row) -> dict:
        mems = members_by_team.get(t["id"], [])
        mems_sorted = sorted(mems, key=lambda m: m["ordinal"])
        return {
            "name": t["name"],
            "location": t["location"],
            "curator": (t["curator"] or "").strip(),
            "members": [
                {
                    "ordinal": m["ordinal"],
                    "rank": m["rank"],
                    "fio": m["fio"],
                    "group": m["study_group"],
                }
                for m in mems_sorted
            ],
        }

    teams_das = [team_dict(t) for t in teams if (t["curator"] or "").strip() == "ДАС и ТПВ"]
    teams_hta = [team_dict(t) for t in teams if (t["curator"] or "").strip() == "ХТА"]

    # Показывать строки «Ответственный …» только если есть соответствующие команды
    show_resp_das = len(teams_das) > 0
    show_resp_hta = len(teams_hta) > 0

    return {
        "comp": {
            "title": comp["title"],
            "sponsor": comp["sponsor"] or "-",
            "format": comp["format"],       # "онлайн" / "офлайн"
            "dates_text": comp["dates_text"]  # строго "DD.MM.YYYY-DD.MM.YYYY"
        },
        # Строгое форматирование дат по ТЗ:
        # 1 день → "с 08:00 до 21:00 ..."
        # 2 дня → "с 08:00 ... и с 8:00 ..."
        # 3 дня → "с 14:00 ..., с 8:00 ... и с 8:00 ..."
        # >3 дней → "с 14:00 до 21:00 в период с ... по ..."
        "dates_with_times": human_dates_with_times(comp["dates_text"]),
        "teams_das": teams_das,
        "teams_hta": teams_hta,
        "show_resp_das": show_resp_das,
        "show_resp_hta": show_resp_hta,
    }

def render_report(comp_id: int, template_name: str = "report_template.docx") -> str:
    tpl_path = os.path.join(settings.TEMPLATES_DIR, template_name)
    if not os.path.exists(tpl_path):
        raise FileNotFoundError(f"Шаблон не найден: {tpl_path}")
    doc = DocxTemplate(tpl_path)
    context = build_context(comp_id)
    doc.render(context)
    out_path = os.path.join(settings.REPORTS_DIR, f"report_comp_{comp_id}.docx")
    doc.save(out_path)
    return out_path
