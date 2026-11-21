"""Render a Site into a single self-contained index.html (CSS inlined) plus copied photos."""

from __future__ import annotations

import json
import shutil
from datetime import date
from importlib import resources
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

from jinja2 import Environment, PackageLoader, select_autoescape

from .config import Site
from .hours import DAY_NAMES, DAYS, SCHEMA_DAYS, day_label, fmt_hhmm

GOOGLE_FONTS = {
    "warm": "family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Nunito+Sans:wght@400;600;700",
    "clean": "family=Plus+Jakarta+Sans:wght@400;500;600;700;800",
    "bold": "family=Archivo:wght@400;600&family=Archivo+Black",
}


# ---- color helpers: keep the brand color readable on each theme's background ----

def _rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02x}" for c in rgb)


def luminance(hex_color: str) -> float:
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in _rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _mix(hex_color: str, target: str, t: float) -> str:
    a, b = _rgb(hex_color), _rgb(target)
    return _hex((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t))


def readable_on(color: str, background: str, ratio: float = 4.5) -> str:
    """Shift ``color`` toward black or white until it reaches ``ratio`` against ``background``."""
    target = "#000000" if luminance(background) > 0.4 else "#ffffff"
    t = 0.0
    out = color
    while contrast(out, background) < ratio and t < 1:
        t += 0.05
        out = _mix(color, target, t)
    return out


def on_color(background: str) -> str:
    """Black or white text, whichever reads better on ``background``."""
    dark = contrast("#111111", background) >= contrast("#ffffff", background)
    return "#111111" if dark else "#ffffff"


def palette(site: Site) -> dict[str, str]:
    brand = site.color if len(site.color) == 7 else _hex(_rgb(site.color))
    # Solid buttons use a brand shade that carries white or near-black text at 4.5:1.
    button = brand
    if contrast(on_color(button), button) < 4.5:
        button = readable_on(brand, "#ffffff", 4.6)
    return {
        "brand": brand,
        "button": button,
        "on_button": on_color(button),
        "ink_light": readable_on(brand, "#ffffff", 4.6),
        "ink_dark": readable_on(brand, "#111113", 4.6),
        "tint": _mix(brand, "#ffffff", 0.86),
        "tint_dark": _mix(brand, "#0b0b0d", 0.8),
    }


# ---- structured data ----

def json_ld(site: Site) -> dict[str, Any]:
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": site.schema_type,
        "name": site.name,
        "telephone": site.phone,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": site.address.street,
            "addressLocality": site.town,
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": SCHEMA_DAYS[i],
                "opens": fmt_hhmm(span.open),
                "closes": fmt_hhmm(span.close),
            }
            for i, spans in enumerate(site.hours)
            for span in spans
        ],
    }
    if site.address.region:
        data["address"]["addressRegion"] = site.address.region
    if site.address.postal_code:
        data["address"]["postalCode"] = site.address.postal_code
    desc = site.description or site.tagline
    if desc:
        data["description"] = desc
    if site.email:
        data["email"] = site.email
    if site.url:
        data["url"] = site.url
    if site.price_range:
        data["priceRange"] = site.price_range
    if site.links:
        data["sameAs"] = list(site.links.values())
    if site.photos:
        data["image"] = [p.src for p in site.photos]
    if site.services:
        data["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Services",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "itemOffered": {"@type": "Service", "name": s.name},
                    **({"description": s.description} if s.description else {}),
                }
                for s in site.services
            ],
        }
    return data


def _hours_script_data(site: Site) -> str:
    payload = {
        "tz": site.timezone,
        "days": [[[s.open, s.close] for s in spans] for spans in site.hours],
    }
    return json.dumps(payload, separators=(",", ":"))


def _script_json(data: object) -> str:
    """JSON safe to place inside a <script> element."""
    return json.dumps(data, indent=2, ensure_ascii=False).replace("</", "<\\/")


def _env() -> Environment:
    return Environment(
        loader=PackageLoader("local_business_site", "templates"),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _theme_css(theme: str) -> str:
    themes = resources.files("local_business_site") / "themes"
    return (themes / "base.css").read_text(encoding="utf-8") + (themes / f"{theme}.css").read_text(
        encoding="utf-8"
    )


def _photos(site: Site, out_dir: Path) -> list[dict[str, str]]:
    result = []
    for i, photo in enumerate(site.photos):
        src = photo.src
        if not src.startswith(("https://", "http://")):
            source = (site.base_dir / src).resolve()
            if not source.is_file():
                raise FileNotFoundError(f"photo not found: {source}")
            dest = out_dir / "photos" / f"{i + 1}{source.suffix.lower()}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            src = f"photos/{dest.name}"
        result.append({"src": src, "alt": photo.alt})
    return result


def render(site: Site, theme: str | None = None, photos: list[dict[str, str]] | None = None) -> str:
    theme = theme or site.theme
    query = quote_plus(f"{site.name}, {site.full_address}")
    if photos is None:
        photos = [{"src": p.src, "alt": p.alt} for p in site.photos]
    description = site.description or (
        f"{site.name}: {site.tagline} {site.type.capitalize()} in {site.town}."
        if site.tagline
        else f"{site.name}, {site.type} in {site.town}. Hours, services and directions."
    )
    return _env().get_template("site.html.j2").render(
        site=site,
        theme=theme,
        css=_theme_css(theme),
        fonts=GOOGLE_FONTS[theme],
        colors=palette(site),
        description=description.strip(),
        photos=photos,
        week=[
            {"key": DAYS[i], "name": DAY_NAMES[i], "label": day_label(spans)}
            for i, spans in enumerate(site.hours)
        ],
        hours_json=_hours_script_data(site),
        json_ld=_script_json(json_ld(site)),
        directions=f"https://www.google.com/maps/search/?api=1&query={query}",
        map_embed=f"https://www.google.com/maps?q={query}&output=embed",
        year=date.today().year,
    )


def build(site: Site, out_dir: Path, theme: str | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    html = render(site, theme, _photos(site, out_dir))
    index = out_dir / "index.html"
    index.write_text(html, encoding="utf-8")
    return index
