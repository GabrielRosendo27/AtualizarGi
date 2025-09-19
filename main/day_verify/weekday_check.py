from datetime import datetime
from typing import Iterable, List


_DAY_NAME_TO_INT = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

_INT_TO_NAME = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


def _parse_token(tok: str) -> int:
    tok = str(tok).strip().lower()
    if not tok:
        raise ValueError("empty token")
    
    if tok.isdigit():
        n = int(tok)
        if 0 <= n <= 6:
            return n
        if 1 <= n <= 7:
            return n - 1
        raise ValueError(f"day number out of range: {tok}")
    
    if tok in _DAY_NAME_TO_INT:
        return _DAY_NAME_TO_INT[tok]
    
    norm = tok.replace("-", "").replace(".", "")
    if norm in _DAY_NAME_TO_INT:
        return _DAY_NAME_TO_INT[norm]
    raise ValueError(f"unknown day token: {tok}")


def parse_allowed_days(spec) -> List[int]:
    if spec is None:
        return []
    if isinstance(spec, (list, tuple)):
        toks = [str(x) for x in spec]
    else:
        toks = [t for t in str(spec).replace(";", ",").split(",") if t.strip() != ""]
    vals = []
    for t in toks:
        vals.append(_parse_token(t))
    return sorted(set(vals))


def allowed_days_to_str(days: Iterable[int]) -> str:
    return ", ".join(_INT_TO_NAME.get(d, str(d)) for d in sorted(days))


def should_run_today(allowed_spec=None, now: datetime = None) -> bool:
    now = now or datetime.now()
    today = now.weekday()  
    try:
        allowed = parse_allowed_days(allowed_spec)
    except Exception:
        allowed = []
    return today in allowed
