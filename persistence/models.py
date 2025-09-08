from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Competition:
    id: int
    title: str
    sponsor: Optional[str]
    dates_text: str
    format: str
    link: Optional[str]
    description: str
    end_date: Optional[str]   # ISO YYYY-MM-DD, если когда-то начнёте сохранять
    created_at: str

@dataclass
class Team:
    id: int
    competition_id: int
    name: str
    member_count: int
    captain_index: int
    location: str
    curator: str
    user_id: Optional[int]
    created_at: str

@dataclass
class Member:
    id: int
    team_id: int
    ordinal: int
    rank: str
    fio: str
    study_group: str

@dataclass
class Result:
    id: int
    competition_id: int
    team_id: int
    place: int
    presentation_path: Optional[str]
    repo_url: Optional[str]
    comment: Optional[str]
    submitted_at: str

@dataclass
class Suggestion:
    id: int
    user_id: int
    title: str
    sponsor: str
    dates_text: str
    format: str
    link: Optional[str]
    status: str
    created_at: str