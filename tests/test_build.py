from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from local_business_site.build import build, contrast, json_ld, palette, render
from local_business_site.cli import main
from local_business_site.config import THEMES, load, parse

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
SECTIONS = (
    'class="hero"',
    'id="services"',
    'id="hours"',
    'id="visit"',
    'id="contact"',
    "<footer",
    'href="tel:5550100000"',
    "google.com/maps",
    '<meta name="description"',
    'property="og:title"',
    'id="hours-data"',
    "prefers-reduced-motion",
)


def ld_from(html: str) -> dict[str, Any]:
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    assert m
    data: dict[str, Any] = json.loads(m.group(1))
    return data


@pytest.mark.parametrize("theme", THEMES)
def test_every_theme_builds_with_required_sections(
    data: dict[str, Any], theme: str, tmp_path: Path
) -> None:
    html = build(parse(data), tmp_path, theme).read_text(encoding="utf-8")
    assert f'class="theme-{theme}"' in html
    for needle in SECTIONS:
        assert needle in html, needle
    assert html.count("<tr data-day=") == 7
    assert chr(0x2014) not in html  # no em dashes in output


def test_json_ld_fields(data: dict[str, Any]) -> None:
    ld = ld_from(render(parse(data)))
    assert ld["@context"] == "https://schema.org"
    assert ld["@type"] == "Bakery"
    assert ld["name"] == "Test Bakery"
    assert ld["telephone"] == "(555) 010-0000"
    assert ld["address"]["@type"] == "PostalAddress"
    assert ld["address"]["addressLocality"] == "Sampleton"
    assert ld["address"]["postalCode"] == "00000"
    specs = ld["openingHoursSpecification"]
    tuesday = {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": "https://schema.org/Tuesday",
        "opens": "07:00",
        "closes": "15:00",
    }
    assert tuesday in specs
    assert len(specs) == 3  # Tuesday plus two Friday ranges
    assert ld["sameAs"] == ["https://facebook.com/example"]
    assert ld["hasOfferCatalog"]["itemListElement"][0]["itemOffered"]["name"] == "Loaf"


def test_json_ld_escapes_script_close(data: dict[str, Any]) -> None:
    data["tagline"] = "</script><b>hi"
    html = render(parse(data))
    assert ld_from(html)["description"] == "</script><b>hi"
    assert "&lt;/script&gt;" in html


def test_json_ld_overnight_close_is_clock_time(data: dict[str, Any]) -> None:
    data["hours"] = {"sat": "18:00-2:00"}
    spec = json_ld(parse(data))["openingHoursSpecification"][0]
    assert (spec["opens"], spec["closes"]) == ("18:00", "02:00")


@pytest.mark.parametrize("color", ["#f5a524", "#ffff00", "#2f7d6d", "#111111", "#fff"])
def test_palette_keeps_contrast(data: dict[str, Any], color: str) -> None:
    data["color"] = color
    p = palette(parse(data))
    assert contrast(p["on_button"], p["button"]) >= 4.5
    assert contrast(p["ink_light"], "#ffffff") >= 4.5
    assert contrast(p["ink_dark"], "#111113") >= 4.5


def test_photos_are_copied(data: dict[str, Any], tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    for i in range(3):
        (src / f"p{i}.JPG").write_bytes(b"x")
    data["photos"] = ["p0.JPG", {"src": "p1.JPG", "alt": "Front counter"}, "p2.JPG"]
    out = tmp_path / "out"
    html = build(parse(data, base_dir=src), out).read_text(encoding="utf-8")
    assert (out / "photos" / "1.jpg").exists()
    assert 'alt="Front counter"' in html
    assert 'id="gallery"' in html


def test_map_off_shows_link_card(data: dict[str, Any]) -> None:
    data["map"] = False
    html = render(parse(data))
    assert "<iframe" not in html
    assert "map-card" in html


@pytest.mark.parametrize("name", ["bakery", "auto-repair", "hair-salon"])
def test_examples_build(name: str, tmp_path: Path) -> None:
    site = load(EXAMPLES / f"{name}.yml")
    assert "555" in site.phone
    assert build(site, tmp_path).exists()


def test_cli_new_then_build(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cfg = tmp_path / "site.yml"
    assert main(["new", str(cfg)]) == 0
    assert main(["new", str(cfg)]) == 1  # refuses to overwrite
    assert main(["build", str(cfg), "-o", str(tmp_path / "out"), "--theme", "bold"]) == 0
    assert "bold theme" in capsys.readouterr().out
    assert (tmp_path / "out" / "index.html").exists()


def test_cli_build_reports_config_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cfg = tmp_path / "site.yml"
    cfg.write_text("name: X\n", encoding="utf-8")
    assert main(["build", str(cfg)]) == 2
    assert "`phone` is required" in capsys.readouterr().err
