import os, sqlite3
from contextlib import closing
from docxtpl import DocxTemplate
from config import settings

def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def human_dates_with_times(dates_text: str) -> str:
    parts = [p.strip() for p in dates_text.replace("и", ",").split(",") if p.strip()]
    return ", ".join([f"с 08:00 до 21:00 {d} года" for d in parts])

def build_context(comp_id: int) -> dict:
    with closing(_db()) as conn:
        comp = conn.execute("SELECT * FROM competitions WHERE id=?", (comp_id,)).fetchone()
        teams = conn.execute("SELECT * FROM teams WHERE competition_id=? ORDER BY id", (comp_id,)).fetchall()
        members_by_team = {
            t["id"]: conn.execute("SELECT * FROM members WHERE team_id=? ORDER BY ordinal", (t["id"],)).fetchall()
            for t in teams
        }

    def team_dict(t):
        return {
            "name": t["name"],
            "location": t["location"],
            "curator": t["curator"],
            "members": [
                {"ordinal": m["ordinal"], "rank": m["rank"], "fio": m["fio"], "group": m["study_group"]}
                for m in members_by_team[t["id"]]
            ],
        }

    teams_das = [team_dict(t) for t in teams if t["curator"] == "ДАС и ТПВ"]
    teams_hta = [team_dict(t) for t in teams if t["curator"] == "ХТА"]

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