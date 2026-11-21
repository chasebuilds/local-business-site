"""Opening hours: parsing, display labels and the "open now" rule.

The same rule runs in the page's small inline script; tests pin it down here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")
DAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
SCHEMA_DAYS = tuple(f"https://schema.org/{d}" for d in DAY_NAMES)

_TIME = re.compile(r"^\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*$", re.IGNORECASE)


class HoursError(ValueError):
    pass


@dataclass(frozen=True)
class Span:
    """Minutes after midnight. ``close`` is above 1440 when a span runs past midnight."""

    open: int
    close: int


def parse_time(text: str) -> int:
    m = _TIME.match(text)
    if not m:
        raise HoursError(f"'{text.strip()}' is not a time like 9:00, 17:30 or 5pm")
    hour, minute, ampm = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
    if minute > 59:
        raise HoursError(f"'{text.strip()}' has minutes above 59")
    if ampm:
        if not 1 <= hour <= 12:
            raise HoursError(f"'{text.strip()}' needs an hour from 1 to 12 with am/pm")
        hour = hour % 12 + (12 if ampm == "pm" else 0)
    elif hour > 24 or (hour == 24 and minute):
        raise HoursError(f"'{text.strip()}' is past 24:00")
    return hour * 60 + minute


def parse_day(value: object) -> list[Span]:
    """Parse '9:00-17:00', '8am-12pm, 1pm-5pm' or 'closed' into spans."""
    if value is None or value is False:
        return []
    text = str(value).strip()
    if text.lower() in {"", "closed", "off"}:
        return []
    spans: list[Span] = []
    for part in text.split(","):
        bits = re.split(r"\s*(?:-|–|to)\s*", part.strip(), maxsplit=1)
        if len(bits) != 2:
            raise HoursError(f"'{part.strip()}' is not a range like 9:00-17:00 or 'closed'")
        start, end = parse_time(bits[0]), parse_time(bits[1])
        if end == start:
            raise HoursError(f"'{part.strip()}' opens and closes at the same time")
        spans.append(Span(start, end if end > start else end + 1440))
    spans.sort(key=lambda s: s.open)
    return spans


def fmt_time(minutes: int) -> str:
    minutes %= 1440
    hour, minute = divmod(minutes, 60)
    suffix = "AM" if hour < 12 else "PM"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d} {suffix}" if minute else f"{hour12} {suffix}"


def fmt_hhmm(minutes: int) -> str:
    hour, minute = divmod(minutes % 1440, 60)
    return f"{hour:02d}:{minute:02d}"


def day_label(spans: list[Span]) -> str:
    if not spans:
        return "Closed"
    return ", ".join(f"{fmt_time(s.open)} – {fmt_time(s.close)}" for s in spans)


Week = list[list[Span]]


def is_open(week: Week, weekday: int, minute: int) -> bool:
    """``weekday`` 0 is Monday, ``minute`` is minutes after midnight."""
    if any(s.open <= minute < s.close for s in week[weekday]):
        return True
    yesterday = week[(weekday - 1) % 7]
    return any(s.close > 1440 and minute + 1440 < s.close for s in yesterday)


def status(week: Week, when: datetime) -> str:
    """Short status line, e.g. 'Open now, closes 5 PM' or 'Closed, opens Tue 7 AM'."""
    wd, minute = when.weekday(), when.hour * 60 + when.minute
    for s in week[wd]:
        if s.open <= minute < s.close:
            return f"Open now, closes {fmt_time(s.close)}"
    for s in week[(wd - 1) % 7]:
        if s.close > 1440 and minute + 1440 < s.close:
            return f"Open now, closes {fmt_time(s.close)}"
    for offset in range(8):
        day = (wd + offset) % 7
        for s in week[day]:
            if offset == 0 and s.open <= minute:
                continue
            when_text = "today" if offset == 0 else DAY_NAMES[day][:3]
            return f"Closed, opens {when_text} {fmt_time(s.open)}"
    return "Closed"
