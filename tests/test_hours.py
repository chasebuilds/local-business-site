from __future__ import annotations

from datetime import datetime

import pytest

from local_business_site.hours import (
    HoursError,
    Span,
    day_label,
    is_open,
    parse_day,
    parse_time,
    status,
)


def week(**days: str) -> list[list[Span]]:
    order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    return [parse_day(days.get(d, "closed")) for d in order]


@pytest.mark.parametrize(
    ("text", "minutes"),
    [("9:00", 540), ("17:30", 1050), ("5pm", 1020), ("12am", 0), ("12pm", 720), ("9:15 AM", 555)],
)
def test_parse_time(text: str, minutes: int) -> None:
    assert parse_time(text) == minutes


@pytest.mark.parametrize("bad", ["25:00", "9:75", "13pm", "noon", ""])
def test_parse_time_rejects(bad: str) -> None:
    with pytest.raises(HoursError):
        parse_time(bad)


def test_parse_day_forms() -> None:
    assert parse_day("closed") == []
    assert parse_day(None) == []
    assert parse_day("9:00-17:00") == [Span(540, 1020)]
    assert parse_day("13:00-17:00, 8:00-12:00") == [Span(480, 720), Span(780, 1020)]
    assert parse_day("18:00-2:00") == [Span(1080, 1560)]  # past midnight


def test_parse_day_errors() -> None:
    with pytest.raises(HoursError, match="not a range"):
        parse_day("9:00")
    with pytest.raises(HoursError, match="same time"):
        parse_day("9:00-9:00")


def test_day_label() -> None:
    assert day_label([]) == "Closed"
    assert day_label(parse_day("7:30-14:00")) == "7:30 AM – 2 PM"


def test_is_open_basic() -> None:
    w = week(tue="9:00-17:00")
    assert is_open(w, 1, 9 * 60)
    assert is_open(w, 1, 16 * 60 + 59)
    assert not is_open(w, 1, 17 * 60)  # the closing minute counts as closed
    assert not is_open(w, 1, 8 * 60 + 59)
    assert not is_open(w, 0, 12 * 60)


def test_is_open_lunch_break() -> None:
    w = week(fri="8:00-12:00, 13:00-17:00")
    assert is_open(w, 4, 11 * 60)
    assert not is_open(w, 4, 12 * 60 + 30)
    assert is_open(w, 4, 13 * 60)


def test_is_open_past_midnight_wraps_into_next_day() -> None:
    w = week(sat="18:00-2:00")
    assert is_open(w, 5, 23 * 60)
    assert is_open(w, 6, 60)  # Sunday 1 AM is still Saturday's shift
    assert not is_open(w, 6, 2 * 60)
    w2 = week(sun="20:00-1:00")
    assert is_open(w2, 0, 30)  # Sunday night shift wraps into Monday


def test_status_lines() -> None:
    w = week(tue="9:00-17:00", thu="10:00-14:00")
    tue = datetime(2026, 11, 17, 12, 0)  # a Tuesday
    assert status(w, tue) == "Open now, closes 5 PM"
    assert status(w, tue.replace(hour=7)) == "Closed, opens today 9 AM"
    assert status(w, tue.replace(hour=18)) == "Closed, opens Thu 10 AM"
    assert status(week(), tue) == "Closed"
