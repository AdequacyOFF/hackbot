from __future__ import annotations
import re
from datetime import datetime
from dateutil import tz

RU_MONTHS = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
    "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
}

TZ = tz.gettz("Europe/Rome")

DATE_RE = re.compile(r"^\s*(\d{1,2})\s+([А-Яа-яЁё]+)(?:\s+(\d{4}))?\s*$")

def _normalize_parts(dates_text: str) -> list[str]:
    # Разобьём по запятым и союзу "и"
    raw = re.split(r",|\s+и\s+", dates_text.replace("И", "и"))
    parts = [p.strip() for p in raw if p.strip()]
    return parts

def _parse_one(part: str, default_year: int | None = None) -> datetime | None:
    m = DATE_RE.match(part)
    if not m:
        return None
    day = int(m.group(1))
    mon_name = m.group(2).lower()
    mon = RU_MONTHS.get(mon_name)
    if not mon:
        return None
    year = int(m.group(3)) if m.group(3) else (default_year or datetime.now(TZ).year)
    try:
        return datetime(year, mon, day, tzinfo=TZ)
    except ValueError:
        return None

def parse_dates_list(dates_text: str) -> list[datetime]:
    parts = _normalize_parts(dates_text)
    year_hint = None
    # если где-то указан год — используем его как «основной»
    for p in parts:
        m = DATE_RE.match(p)
        if m and m.group(3):
            year_hint = int(m.group(3))
            break
    result: list[datetime] = []
    for p in parts:
        dt = _parse_one(p, default_year=year_hint)
        if dt:
            result.append(dt)
    return result

def human_dates_with_times(dates_text: str, start_time: str = "08:00", end_time: str = "21:00",
                           join_with: str = ", ") -> str:
    """Возвращает 'с 08:00 до 21:00 29 марта 2025 года, с 08:00 до 21:00 30 марта 2025 года'."""
    parts = _normalize_parts(dates_text)
    # сохраняем исходные словоформы как в тексте (для месяца),
    # но если нет года — аккуратно допишем его к строке
    dates = parse_dates_list(dates_text)
    chunks: list[str] = []
    for i, dt in enumerate(dates):
        # возьмём исходный месяц словом из parts[i] (для естественности),
        # либо построим из dt, если не получается
        mo = None
        mm = re.search(r"[А-Яа-яЁё]+", parts[i]) if i < len(parts) else None
        if mm:
            mo = mm.group(0)
        # гарантируем год
        year = dt.year
        chunk = f"с {start_time} до {end_time} {dt.day} {mo or _month_to_genitive(dt.month)} {year} года"
        chunks.append(chunk)
    # соединитель: по умолчанию через запятую; хотите « и » — смените join_with=" и "
    return join_with.join(chunks)

def _month_to_genitive(m: int) -> str:
    # обратный словарь
    for name, num in RU_MONTHS.items():
        if num == m:
            return name
    return ""

def infer_last_date(dates_text: str) -> datetime | None:
    dates = parse_dates_list(dates_text)
    return max(dates) if dates else None