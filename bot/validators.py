import re
FIO_RE = re.compile(r"^[А-ЯЁ][а-яё-]+ [А-ЯЁ]\.[ ]?[А-ЯЁ]\.$")
GROUP_RE = re.compile(r"^\d{1,4}(?:/\d{1,4})?$")
def valid_fio(s: str) -> bool: return bool(FIO_RE.match(s.strip()))
def valid_group(s: str) -> bool: return bool(GROUP_RE.match(s.strip()))
def valid_url(s: str) -> bool: return s.startswith(("http://","https://"))