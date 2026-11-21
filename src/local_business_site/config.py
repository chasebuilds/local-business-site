"""Load and validate the site YAML into a typed config. Every problem is collected and
reported at once, each with the field path, so one fix pass is enough."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .hours import DAYS, HoursError, Span, parse_day

THEMES = ("warm", "clean", "bold")

# Free-text business type -> schema.org LocalBusiness subtype.
SCHEMA_TYPES = {
    "bakery": "Bakery",
    "cafe": "CafeOrCoffeeShop",
    "coffee shop": "CafeOrCoffeeShop",
    "restaurant": "Restaurant",
    "pizzeria": "Restaurant",
    "bar": "BarOrPub",
    "auto repair": "AutoRepair",
    "mechanic": "AutoRepair",
    "garage": "AutoRepair",
    "hair salon": "HairSalon",
    "barber": "HairSalon",
    "barbershop": "HairSalon",
    "beauty salon": "BeautySalon",
    "nail salon": "NailSalon",
    "florist": "Florist",
    "plumber": "Plumber",
    "electrician": "Electrician",
    "dentist": "Dentist",
    "gym": "ExerciseGym",
    "pet groomer": "LocalBusiness",
    "hardware store": "HardwareStore",
    "bookstore": "BookStore",
    "clothing store": "ClothingStore",
    "laundromat": "DryCleaningOrLaundry",
    "dry cleaner": "DryCleaningOrLaundry",
}

_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_CHARS = re.compile(r"^[0-9+().\-\s]+$")
_KNOWN = {
    "name", "tagline", "type", "town", "phone", "email", "address", "hours", "timezone",
    "services", "photos", "links", "color", "theme", "description", "map", "url",
    "price_range", "credit",
}


class ConfigError(ValueError):
    def __init__(self, source: str, problems: list[str]):
        self.problems = problems
        lines = "\n".join(f"  - {p}" for p in problems)
        super().__init__(f"{source} has {len(problems)} problem(s):\n{lines}")


@dataclass(frozen=True)
class Service:
    name: str
    price: str = ""
    description: str = ""


@dataclass(frozen=True)
class Photo:
    src: str
    alt: str


@dataclass(frozen=True)
class Address:
    street: str
    region: str = ""
    postal_code: str = ""


@dataclass
class Site:
    name: str
    tagline: str
    type: str
    town: str
    phone: str
    address: Address
    hours: list[list[Span]]
    color: str
    email: str = ""
    description: str = ""
    timezone: str = ""
    services: list[Service] = field(default_factory=list)
    photos: list[Photo] = field(default_factory=list)
    links: dict[str, str] = field(default_factory=dict)
    theme: str = "warm"
    map: bool = True
    url: str = ""
    price_range: str = ""
    credit: bool = True
    base_dir: Path = field(default_factory=Path)

    @property
    def schema_type(self) -> str:
        key = self.type.strip().lower()
        if key in SCHEMA_TYPES:
            return SCHEMA_TYPES[key]
        if self.type in SCHEMA_TYPES.values():
            return self.type
        return "LocalBusiness"

    @property
    def phone_href(self) -> str:
        return "tel:" + re.sub(r"[^0-9+]", "", self.phone)

    @property
    def full_address(self) -> str:
        tail = " ".join(p for p in (self.address.region, self.address.postal_code) if p)
        return ", ".join(p for p in (self.address.street, self.town, tail) if p)


def _text(data: dict[str, Any], key: str, problems: list[str], required: bool = False) -> str:
    value = data.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        if required:
            problems.append(f"`{key}` is required")
        return ""
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        problems.append(f"`{key}` must be text, got {type(value).__name__}")
        return ""
    return str(value).strip()


def parse(data: object, source: str = "site.yml", base_dir: Path | None = None) -> Site:
    if not isinstance(data, dict):
        raise ConfigError(source, ["the file must be a YAML mapping of fields (name: ..., ...)"])
    problems: list[str] = []
    for key in data:
        if key not in _KNOWN:
            problems.append(f"`{key}` is not a known field (known: {', '.join(sorted(_KNOWN))})")

    name = _text(data, "name", problems, required=True)
    tagline = _text(data, "tagline", problems)
    btype = _text(data, "type", problems, required=True)
    town = _text(data, "town", problems, required=True)
    phone = _text(data, "phone", problems, required=True)
    if phone and (not _PHONE_CHARS.match(phone) or len(re.sub(r"\D", "", phone)) < 7):
        problems.append(f"`phone` '{phone}' should look like (555) 010-1234")
    email = _text(data, "email", problems)
    if email and not _EMAIL.match(email):
        problems.append(f"`email` '{email}' is not an email address")

    raw_addr = data.get("address")
    address = Address("")
    if isinstance(raw_addr, str) and raw_addr.strip():
        address = Address(raw_addr.strip())
    elif isinstance(raw_addr, dict):
        street = str(raw_addr.get("street") or "").strip()
        if not street:
            problems.append("`address.street` is required")
        address = Address(
            street,
            str(raw_addr.get("region") or "").strip(),
            str(raw_addr.get("postal_code") or "").strip(),
        )
    else:
        problems.append("`address` is required (a street line, or street/region/postal_code)")

    hours: list[list[Span]] = [[] for _ in DAYS]
    raw_hours = data.get("hours")
    if not isinstance(raw_hours, dict) or not raw_hours:
        problems.append("`hours` is required: one line per day, e.g. mon: 9:00-17:00")
    else:
        for key, value in raw_hours.items():
            day = str(key).strip().lower()[:3]
            if day not in DAYS:
                problems.append(f"`hours.{key}` is not a day (use mon, tue, ... sun)")
                continue
            try:
                hours[DAYS.index(day)] = parse_day(value)
            except HoursError as exc:
                problems.append(f"`hours.{key}`: {exc}")

    services: list[Service] = []
    raw_services = data.get("services") or []
    if not isinstance(raw_services, list):
        problems.append("`services` must be a list")
    else:
        for i, item in enumerate(raw_services):
            if isinstance(item, str) and item.strip():
                services.append(Service(item.strip()))
            elif isinstance(item, dict) and str(item.get("name") or "").strip():
                price = item.get("price")
                price_text = "" if price is None else str(price).strip()
                if isinstance(price, (int, float)) and not isinstance(price, bool):
                    price_text = f"${price:,.2f}".replace(".00", "")
                services.append(
                    Service(
                        str(item["name"]).strip(),
                        price_text,
                        str(item.get("description") or "").strip(),
                    )
                )
            else:
                problems.append(f"`services[{i}]` needs a name")

    photos: list[Photo] = []
    raw_photos = data.get("photos") or []
    if not isinstance(raw_photos, list):
        problems.append("`photos` must be a list")
    else:
        if raw_photos and not 3 <= len(raw_photos) <= 6:
            problems.append(f"`photos` needs 3 to 6 photos or none, got {len(raw_photos)}")
        for i, item in enumerate(raw_photos):
            if isinstance(item, str) and item.strip():
                photos.append(Photo(item.strip(), f"{name} photo {i + 1}"))
            elif isinstance(item, dict) and str(item.get("src") or "").strip():
                alt = str(item.get("alt") or f"{name} photo {i + 1}").strip()
                photos.append(Photo(str(item["src"]).strip(), alt))
            else:
                problems.append(f"`photos[{i}]` needs a src (a file path or https URL)")

    links: dict[str, str] = {}
    raw_links = data.get("links") or {}
    if not isinstance(raw_links, dict):
        problems.append("`links` must be a mapping like facebook: https://...")
    else:
        for key, value in raw_links.items():
            url = str(value or "").strip()
            if not url:
                continue
            if not url.startswith(("https://", "http://")):
                problems.append(f"`links.{key}` must start with https://")
            links[str(key).lower()] = url

    color = _text(data, "color", problems) or "#b5523b"
    if not _HEX.match(color):
        problems.append(f"`color` '{color}' must be a hex color like #b5523b")

    theme = _text(data, "theme", problems) or "warm"
    if theme not in THEMES:
        problems.append(f"`theme` '{theme}' must be one of: {', '.join(THEMES)}")

    url = _text(data, "url", problems)
    if url and not url.startswith("https://"):
        problems.append("`url` must start with https://")

    if problems:
        raise ConfigError(source, problems)
    return Site(
        name=name,
        tagline=tagline,
        type=btype,
        town=town,
        phone=phone,
        address=address,
        hours=hours,
        color=color,
        email=email,
        description=_text(data, "description", problems),
        timezone=_text(data, "timezone", problems),
        services=services,
        photos=photos,
        links=links,
        theme=theme,
        map=bool(data.get("map", True)),
        url=url,
        price_range=_text(data, "price_range", problems),
        credit=bool(data.get("credit", True)),
        base_dir=base_dir or Path("."),
    )


def load(path: Path) -> Site:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(str(path), [f"cannot read the file: {exc.strerror}"]) from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise ConfigError(str(path), [f"is not valid YAML{where}"]) from exc
    return parse(data, str(path), path.parent)
