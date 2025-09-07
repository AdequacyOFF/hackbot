import re
from datetime import datetime, timedelta, time
from typing import Optional
from config import settings


MONTHS = {
'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
}


def parse_end_date_from_dates_text(dates_text: str) -> Optional[str]:
parts = [p.strip() for p in dates_text.replace("и", ",").split(",") if p.strip()]
if not parts:
return None
last = parts[-1]
m = re.match(r"^(\d{1,2}) ([а-яё]+)(?: (\d{4}))?$", last, re.IGNORECASE)
if not m:
return None
day = int(m.group(1))
month_name = m.group(2).lower()
year = int(m.group(3)) if m.group(3) else datetime.now(tz=settings.TZ).year
month = MONTHS.get(month_name)
if not month:
return None
try:
d = datetime(year, month, day)
return d.strftime("%Y-%m-%d")
except Exception:
return None




def deadline_from_end_date(end_date_str: Optional[str]) -> Optional[datetime]:
if not end_date_str:
return None
d = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=settings.TZ)
next_day = (d + timedelta(days=1)).date()
return datetime.combine(next_day, time(0, 0), tzinfo=settings.TZ)




def human_dates_with_times(dates_text: str) -> str:
parts = [p.strip() for p in dates_text.replace("и", ",").split(",") if p.strip()]
chunks = [f"с 08:00 до 21:00 {d} года" for d in parts]
return ", ".join(chunks)