from __future__ import annotations
import os
import sqlite3
from contextlib import closing
from typing import Iterable, Optional
from config import settings
from .db import connect

# ---------- Competitions ----------
def competitions_list(include_desc: bool = False) -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        cols = "*" if include_desc else "id, title, sponsor, dates_text, format, link, end_date, created_at"
        return conn.execute(f"SELECT {cols} FROM competitions ORDER BY id DESC").fetchall()

def competition_get(comp_id: int) -> Optional[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute("SELECT * FROM competitions WHERE id=?", (comp_id,)).fetchone()

def competition_add(title: str, sponsor: str, dates_text: str, fmt: str, link: str | None, description: str = "", end_date: str | None = None) -> int:
    with closing(connect()) as conn:
        cur = conn.execute(
            "INSERT INTO competitions(title, sponsor, dates_text, format, link, description, end_date, created_at) "
            "VALUES(?,?,?,?,?,?,?, datetime('now'))",
            (title.strip(), sponsor.strip() if sponsor else None, dates_text.strip(), fmt.strip(), (link or None), description, end_date)
        )
        conn.commit()
        return cur.lastrowid

def competition_delete(comp_id: int) -> None:
    with closing(connect()) as conn:
        conn.execute("DELETE FROM competitions WHERE id=?", (comp_id,))
        conn.commit()

# ---------- Teams & Members ----------
def teams_by_competition(comp_id: int) -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute(
            "SELECT * FROM teams WHERE competition_id=? ORDER BY id", (comp_id,)
        ).fetchall()

def team_add(competition_id: int, name: str, member_count: int, captain_index: int,
             location: str, curator: str, user_id: int | None) -> int:
    with closing(connect()) as conn:
        cur = conn.execute(
            "INSERT INTO teams(competition_id, name, member_count, captain_index, location, curator, user_id, created_at) "
            "VALUES(?,?,?,?,?,?,?, datetime('now'))",
            (competition_id, name.strip(), member_count, captain_index, location.strip(), curator.strip(), user_id)
        )
        conn.commit()
        return cur.lastrowid

def team_get(team_id: int) -> Optional[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute("SELECT * FROM teams WHERE id=?", (team_id,)).fetchone()

def team_delete(team_id: int) -> None:
    with closing(connect()) as conn:
        conn.execute("DELETE FROM teams WHERE id=?", (team_id,))
        conn.commit()

def members_add_bulk(team_id: int, members: Iterable[tuple[int, str, str, str]]) -> None:
    # members: (ordinal, rank, fio, study_group)
    with closing(connect()) as conn:
        conn.executemany(
            "INSERT INTO members(team_id, ordinal, rank, fio, study_group) VALUES(?,?,?,?,?)",
            [(team_id, o, r, f, g) for (o, r, f, g) in members]
        )
        conn.commit()

def members_by_team(team_id: int) -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute("SELECT * FROM members WHERE team_id=? ORDER BY ordinal", (team_id,)).fetchall()

# ---------- Results ----------
def result_add(competition_id: int, team_id: int, place: int, presentation_path: str | None,
               repo_url: str | None, comment: str) -> int:
    with closing(connect()) as conn:
        cur = conn.execute(
            "INSERT INTO results(competition_id, team_id, place, presentation_path, repo_url, comment, submitted_at) "
            "VALUES(?,?,?,?,?,?, datetime('now'))",
            (competition_id, team_id, place, presentation_path, repo_url, comment.strip())
        )
        conn.commit()
        return cur.lastrowid

def results_by_competition(comp_id: int) -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute(
            "SELECT r.*, t.name AS team_name FROM results r JOIN teams t ON t.id=r.team_id WHERE r.competition_id=? ORDER BY r.place",
            (comp_id,)
        ).fetchall()

def result_for_team(team_id: int) -> Optional[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute("SELECT * FROM results WHERE team_id=? LIMIT 1", (team_id,)).fetchone()

# ---------- Suggestions ----------
def suggestion_add(user_id: int, title: str, sponsor: str, dates_text: str, fmt: str, link: str | None) -> int:
    with closing(connect()) as conn:
        cur = conn.execute(
            "INSERT INTO suggestions(user_id, title, sponsor, dates_text, format, link, status, created_at) "
            "VALUES(?,?,?,?,?,?,'pending', datetime('now'))",
            (user_id, title.strip(), sponsor.strip(), dates_text.strip(), fmt.strip(), (link or None))
        )
        conn.commit()
        return cur.lastrowid

def suggestions_list(status: str = "pending") -> list[sqlite3.Row]:
    with closing(connect()) as conn:
        return conn.execute(
            "SELECT * FROM suggestions WHERE status=? ORDER BY id", (status,)
        ).fetchall()

def suggestion_update_status(sug_id: int, status: str) -> None:
    with closing(connect()) as conn:
        conn.execute("UPDATE suggestions SET status=? WHERE id=?", (status, sug_id))
        conn.commit()