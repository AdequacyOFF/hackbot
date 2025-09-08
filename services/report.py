import os, sqlite3
from contextlib import closing
from docxtpl import DocxTemplate
from config import settings
from services.dates import human_dates_with_times

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
        # на всякий — сортируем по ordinal
        mems_sorted = sorted(mems, key=lambda m: m["ordinal"])
        return {
            "name": t["name"],
            "location": t["location"],
            "curator": t["curator"],
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

    def _curator(v: str | None) -> str:
        return (v or "").strip()

    teams_das = [team_dict(t) for t in teams if _curator(t["curator"]) == "ДАС и ТПВ"]
    teams_hta = [team_dict(t) for t in teams if _curator(t["curator"]) == "ХТА"]


    return {
        "comp": {
            "title": comp["title"],
            "sponsor": comp["sponsor"] or "-",
            "format": comp["format"],
            "dates_text": comp["dates_text"],
        },
        "dates_with_times": human_dates_with_times(comp["dates_text"]),
        "teams_das": teams_das,
        "teams_hta": teams_hta,
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