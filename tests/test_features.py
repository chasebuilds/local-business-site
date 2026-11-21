"""Conversion features: credit link, testimonials, trust, service area, FAQ, quote button,
mobile bar, title, share image, robots and sitemap."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import pytest

from local_business_site.build import build, json_ld, quote_href, render
from local_business_site.config import DEFAULT_QUOTE_LABEL, ConfigError, parse

CREDIT = (
    '<a class="credit" href="https://github.com/chasebuilds" target="_blank" rel="noopener">'
    "Site by Chase Builds</a>"
)
REVIEWS = [
    {"quote": "Best loaf in town.", "name": "Sam P.", "source": "Google review"},
    {"quote": "Cakes are lovely.", "name": "Rae T."},
]


def ld_blocks(html: str) -> list[dict[str, Any]]:
    found = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    return [json.loads(b) for b in found]


def problems(data: dict[str, Any]) -> list[str]:
    with pytest.raises(ConfigError) as exc:
        parse(data)
    return exc.value.problems


def test_credit_link_is_on_by_default(data: dict[str, Any]) -> None:
    html = render(parse(data))
    assert CREDIT in html


def test_credit_false_removes_it(data: dict[str, Any]) -> None:
    data["credit"] = False
    html = render(parse(data))
    assert "Site by Chase Builds" not in html
    assert "github.com/chasebuilds" not in html


def test_old_yaml_without_new_fields_has_no_new_sections(data: dict[str, Any]) -> None:
    html = render(parse(data))
    for needle in ('id="reviews"', 'class="trust', 'id="area"', 'id="faq"', "?subject="):
        assert needle not in html, needle
    assert len(ld_blocks(html)) == 1


def test_testimonials_render_near_the_top(data: dict[str, Any]) -> None:
    data["testimonials"] = REVIEWS
    html = render(parse(data))
    assert 'id="reviews"' in html
    assert "Best loaf in town." in html
    assert "<span>Google review</span>" in html
    assert "Rae T." in html
    assert html.index('id="reviews"') < html.index('id="services"')
    assert 'href="#reviews"' in html


@pytest.mark.parametrize("count", [1, 5])
def test_testimonials_need_two_to_four(data: dict[str, Any], count: int) -> None:
    data["testimonials"] = [{"quote": "Good.", "name": f"P{i}"} for i in range(count)]
    assert any("2 to 4" in p for p in problems(data))


def test_testimonial_needs_quote_and_name(data: dict[str, Any]) -> None:
    data["testimonials"] = [{"quote": "Good."}, "just text"]
    found = problems(data)
    assert "`testimonials[0]` needs name" in found
    assert "`testimonials[1]` needs quote and name" in found


def test_trust_badges_under_hero(data: dict[str, Any]) -> None:
    data["trust"] = ["Licensed and insured", "Family owned", 1986]
    html = render(parse(data))
    hero = html[html.index('class="hero"') : html.index("</section>")]
    assert '<ul class="trust' in hero
    for badge in ("Licensed and insured", "Family owned", "1986"):
        assert f"<span>{badge}</span>" in hero


def test_trust_must_be_a_list_of_text(data: dict[str, Any]) -> None:
    data["trust"] = "Family owned"
    assert "`trust` must be a list" in problems(data)
    data["trust"] = [{"a": 1}]
    assert "`trust[0]` must be a short piece of text" in problems(data)


def test_service_area_section_and_json_ld(data: dict[str, Any]) -> None:
    data["service_area"] = ["Sampleton", "North County"]
    site = parse(data)
    html = render(site)
    assert 'id="area"' in html
    assert "<span>North County</span>" in html
    assert json_ld(site)["areaServed"] == [
        {"@type": "Place", "name": "Sampleton"},
        {"@type": "Place", "name": "North County"},
    ]


def test_faq_section_and_faqpage_json_ld(data: dict[str, Any]) -> None:
    data["faq"] = [
        {"question": "Do you deliver?", "answer": "Yes, in town."},
        {"question": "Gluten free?", "answer": "Two loaves a day."},
    ]
    html = render(parse(data))
    assert "<summary>Do you deliver?</summary>" in html
    blocks = ld_blocks(html)
    assert blocks[0]["@type"] == "Bakery"
    faq = blocks[1]
    assert faq["@type"] == "FAQPage"
    assert faq["mainEntity"][0] == {
        "@type": "Question",
        "name": "Do you deliver?",
        "acceptedAnswer": {"@type": "Answer", "text": "Yes, in town."},
    }


def test_faq_needs_question_and_answer(data: dict[str, Any]) -> None:
    data["faq"] = [{"question": "Open late?"}]
    assert "`faq[0]` needs answer" in problems(data)


def test_quote_cta_uses_prefilled_email(data: dict[str, Any]) -> None:
    data["quote_cta"] = True
    site = parse(data)
    href = quote_href(site)
    assert site.quote_cta == DEFAULT_QUOTE_LABEL
    assert href.startswith("mailto:hi@example.com?subject=")
    assert "Quote request for Test Bakery" in unquote(href)
    html = render(site)
    assert html.count(DEFAULT_QUOTE_LABEL) == 2  # hero and contact
    assert "mailto:hi@example.com?subject=Quote%20request" in html


def test_quote_cta_sms_with_custom_label(data: dict[str, Any]) -> None:
    data.pop("email")
    data["sms"] = True
    data["quote_cta"] = "Text us for a price"
    site = parse(data)
    assert quote_href(site).startswith("sms:5550100000?&body=")
    assert "Text us for a price" in render(site)


def test_quote_cta_needs_email_or_sms(data: dict[str, Any]) -> None:
    data.pop("email")
    data["quote_cta"] = True
    assert any("needs `email` or `sms: true`" in p for p in problems(data))


def test_quote_cta_off_by_default(data: dict[str, Any]) -> None:
    assert quote_href(parse(data)) == ""


def test_bad_sms_and_quote_values(data: dict[str, Any]) -> None:
    data["sms"] = "yes"
    data["quote_cta"] = 3
    found = problems(data)
    assert "`sms` must be true or false" in found
    assert "`quote_cta` must be true, false or a button label" in found


def test_mobile_bar_has_call_and_directions(data: dict[str, Any]) -> None:
    html = render(parse(data))
    bar = html[html.index('<nav class="mobile-bar"') :]
    bar = bar[: bar.index("</nav>")]
    assert 'href="tel:5550100000"' in bar
    assert "google.com/maps/search" in bar
    assert ".mobile-bar{display:grid" in html  # shown by the phone media query


def test_title_and_meta_include_type_town_and_region(data: dict[str, Any]) -> None:
    html = render(parse(data))
    assert "<title>Test Bakery | Bakery in Sampleton, ST</title>" in html
    assert "Bakery in Sampleton, ST." in html
    data["address"] = {"street": "1 Test Street"}
    assert "<title>Test Bakery | Bakery in Sampleton</title>" in render(parse(data))


def test_favicon_is_brand_initial_svg(data: dict[str, Any]) -> None:
    html = render(parse(data))
    assert '<link rel="icon" href="data:image/svg+xml,' in html
    assert "%3ET%3C/text%3E" in html


def test_canonical_robots_and_sitemap_when_url_set(data: dict[str, Any], tmp_path: Path) -> None:
    data["url"] = "https://example.com/bakery"
    html = build(parse(data), tmp_path).read_text(encoding="utf-8")
    assert '<link rel="canonical" href="https://example.com/bakery">' in html
    robots = (tmp_path / "robots.txt").read_text(encoding="utf-8")
    assert "Sitemap: https://example.com/bakery/sitemap.xml" in robots
    sitemap = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")
    assert "<loc>https://example.com/bakery/</loc>" in sitemap
    assert "<lastmod>" in sitemap


def test_no_robots_or_sitemap_without_url(data: dict[str, Any], tmp_path: Path) -> None:
    html = build(parse(data), tmp_path).read_text(encoding="utf-8")
    assert 'rel="canonical"' not in html
    assert not (tmp_path / "robots.txt").exists()
    assert not (tmp_path / "sitemap.xml").exists()


def test_og_image_field_wins(data: dict[str, Any]) -> None:
    data["og_image"] = "https://example.com/share.jpg"
    html = render(parse(data))
    assert '<meta property="og:image" content="https://example.com/share.jpg">' in html


def test_og_image_falls_back_to_first_photo_with_url(data: dict[str, Any], tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    for i in range(3):
        (src / f"p{i}.jpg").write_bytes(b"x")
    data["photos"] = ["p0.jpg", "p1.jpg", "p2.jpg"]
    data["url"] = "https://example.com/"
    html = build(parse(data, base_dir=src), tmp_path / "out").read_text(encoding="utf-8")
    assert 'og:image" content="https://example.com/photos/1.jpg"' in html


def test_og_image_must_be_https(data: dict[str, Any]) -> None:
    data["og_image"] = "share.jpg"
    assert "`og_image` must be an https:// URL" in problems(data)


def test_tap_targets_are_at_least_44px(data: dict[str, Any]) -> None:
    html = render(parse(data))
    heights = [int(h) for h in re.findall(r"min-height:(\d+)px", html)]
    assert heights and min(heights) >= 44
