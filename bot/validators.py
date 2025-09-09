import re
from datetime import datetime, timedelta
FIO_RE = re.compile(r"^[А-ЯЁ][а-яё-]+ [А-ЯЁ]\.[ ]?[А-ЯЁ]\.$")
GROUP_RE = re.compile(r"^\d{1,4}(?:/\d{1,4})?$")
def valid_fio(s: str) -> bool: return bool(FIO_RE.match(s.strip()))
def valid_group(s: str) -> bool: return bool(GROUP_RE.match(s.strip()))
def valid_url(s: str) -> bool: return s.startswith(("http://","https://"))

DATE_RANGE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}-\d{2}\.\d{2}\.\d{4}$")

def parse_date_range_strict(s: str):
    """
    Строго 'DD.MM.YYYY-DD.MM.YYYY' без пробелов.
    Возвращает (date_start, date_end) или None.
    """
    if not s or " " in s:
        return None
    if not DATE_RANGE_RE.match(s):
        return None
    try:
        d1 = datetime.strptime(s[:10], "%d.%m.%Y").date()
        d2 = datetime.strptime(s[11:], "%d.%m.%Y").date()
        if d1 > d2:
            return None
        return d1, d2
    except Exception:
        return None