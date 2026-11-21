from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture
def data() -> dict[str, Any]:
    return {
        "name": "Test Bakery",
        "tagline": "Bread daily.",
        "type": "bakery",
        "town": "Sampleton",
        "phone": "(555) 010-0000",
        "email": "hi@example.com",
        "address": {"street": "1 Test Street", "region": "ST", "postal_code": "00000"},
        "hours": {"mon": "closed", "tue": "7:00-15:00", "fri": "8am-12pm, 1pm-5pm"},
        "services": [{"name": "Loaf", "price": 8, "description": "Good."}, "Cakes"],
        "links": {"facebook": "https://facebook.com/example"},
        "color": "#c2622d",
    }
