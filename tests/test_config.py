from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from local_business_site.config import ConfigError, load, parse


def problems(data: object) -> list[str]:
    with pytest.raises(ConfigError) as info:
        parse(data)
    return info.value.problems


def test_valid(data: dict[str, Any]) -> None:
    site = parse(data)
    assert site.name == "Test Bakery"
    assert site.schema_type == "Bakery"
    assert site.services[0].price == "$8"
    assert site.services[1].name == "Cakes"
    assert site.phone_href == "tel:5550100000"
    assert site.full_address == "1 Test Street, Sampleton, ST 00000"
    assert len(site.hours[4]) == 2


def test_missing_required_fields_all_reported() -> None:
    text = "\n".join(problems({"tagline": "x"}))
    for key in ("name", "type", "town", "phone", "address", "hours"):
        assert f"`{key}`" in text


def test_not_a_mapping() -> None:
    assert "YAML mapping" in problems(["a", "b"])[0]


def test_bad_values_have_clear_messages(data: dict[str, Any]) -> None:
    data.update(
        color="orange",
        theme="neon",
        email="nope",
        phone="call us",
        photos=["a.jpg"],
        hours={"mon": "9-5pm", "funday": "9:00-10:00", "tue": "nine to five"},
        colour="#fff",
    )
    text = "\n".join(problems(data))
    assert "`color` 'orange' must be a hex color" in text
    assert "`theme` 'neon' must be one of: warm, clean, bold" in text
    assert "`email` 'nope' is not an email address" in text
    assert "`phone`" in text
    assert "3 to 6 photos or none, got 1" in text
    assert "`hours.funday` is not a day" in text
    assert "`hours.tue`" in text
    assert "`colour` is not a known field" in text


def test_error_message_lists_each_problem(data: dict[str, Any]) -> None:
    data["color"] = "red"
    with pytest.raises(ConfigError) as info:
        parse(data, "site.yml")
    assert str(info.value).startswith("site.yml has 1 problem(s):\n  - `color`")


def test_load_reports_yaml_syntax_line(tmp_path: Path) -> None:
    bad = tmp_path / "site.yml"
    bad.write_text("name: x\nhours: [unclosed\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="not valid YAML at line"):
        load(bad)


def test_unknown_type_falls_back_to_local_business(data: dict[str, Any]) -> None:
    data["type"] = "tattoo parlor"
    assert parse(data).schema_type == "LocalBusiness"
