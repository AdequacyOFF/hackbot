from __future__ import annotations
from datetime import datetime, timedelta, date
import re

RU_MONTHS_GEN = [
    None, "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
]

STRICT_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}-\d{2}\.\d{2}\.\d{4}$")

def _fmt_genitive(d: date) -> str:
    return f"{d.day} {RU_MONTHS_GEN[d.month]} {d.year} года"

def _parse_strict_range(s: str) -> tuple[date, date] | None:
    if not s or " " in s or not STRICT_RE.match(s):
        return None
    try:
        d1 = datetime.strptime(s[:10], "%d.%m.%Y").date()
        d2 = datetime.strptime(s[11:], "%d.%m.%Y").date()
        if d1 > d2:
            return None
        return d1, d2
    except Exception:
        return None

def human_dates_with_times(dates_text: str) -> str:
    """
    Вход: строго 'DD.MM.YYYY-DD.MM.YYYY' (без пробелов).
    Выход:
      • 1 день:  'с 08:00 до 21:00 29 марта 2025 года'
      • 2 дня:  'с 08:00 до 21:00 29 марта 2025 года и с 8:00 до 21:00 30 марта 2025 года'
      • 3 дня:  'с 14:00 до 21:00 28 марта 2025 года, с 8:00 до 21:00 29 марта 2025 года и с 8:00 до 21:00 30 марта 2025 года'
      • >3 дней: 'с 14:00 до 21:00 в период с 18 сентября по 2 октября 2025 года'
    """
    rng = _parse_strict_range(dates_text)
    if not rng:
        # если прилетит старый формат, хотя по ТЗ мы его больше не принимаем
        # вернём исходный текст, чтобы не упасть
        return dates_text

    d1, d2 = rng
    days = (d2 - d1).days + 1

    if days == 1:
        return f"с 08:00 до 21:00 {_fmt_genitive(d1)}"
    if days == 2:
        # специально: первый день '08:00', второй — '8:00'
        return f"с 08:00 до 21:00 {_fmt_genitive(d1)} и с 8:00 до 21:00 {_fmt_genitive(d2)}"
    if days == 3:
        mid = d1 + timedelta(days=1)
        return (
            f"с 14:00 до 21:00 {_fmt_genitive(d1)}, "
            f"с 8:00 до 21:00 {_fmt_genitive(mid)} и "
            f"с 8:00 до 21:00 {_fmt_genitive(d2)}"
        )

    # > 3 дней — период
    if d1.year == d2.year:
        return (f"с 14:00 до 21:00 в период с {d1.day} {RU_MONTHS_GEN[d1.month]} "
                f"по {d2.day} {RU_MONTHS_GEN[d2.month]} {d2.year} года")
    else:
        return (f"с 14:00 до 21:00 в период с {d1.day} {RU_MONTHS_GEN[d1.month]} {d1.year} года "
                f"по {d2.day} {RU_MONTHS_GEN[d2.month]} {d2.year} года")

def infer_last_date_iso(dates_text: str) -> str | None:
    rng = _parse_strict_range(dates_text)
    return rng[1].isoformat() if rng else None
