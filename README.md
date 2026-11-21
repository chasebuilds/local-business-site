# local-business-site

[![ci](https://github.com/chasebuilds/local-business-site/actions/workflows/ci.yml/badge.svg)](https://github.com/chasebuilds/local-business-site/actions/workflows/ci.yml) [![pages](https://github.com/chasebuilds/local-business-site/actions/workflows/pages.yml/badge.svg)](https://chasebuilds.github.io/local-business-site/) ![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue) [![MIT license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Live demos:** [all three](https://chasebuilds.github.io/local-business-site/) | [bakery (warm)](https://chasebuilds.github.io/local-business-site/bakery/) | [auto repair (bold)](https://chasebuilds.github.io/local-business-site/auto-repair/) | [hair salon (clean)](https://chasebuilds.github.io/local-business-site/hair-salon/)

Turns one YAML file into a fast, mobile-first, one-page website for a small local business: a hero with call and directions buttons, services with prices, an hours table that highlights today and shows "open now", a map, contact links and a footer. The output is a single `index.html` with the CSS inlined, so it can go on any static host.

The demo businesses are invented. Names, towns, addresses and 555 phone numbers are fictional.

## Three themes

| warm | bold | clean |
|---|---|---|
| ![Bakery demo, warm theme](docs/bakery.png) | ![Auto repair demo, bold theme](docs/auto-repair.png) | ![Hair salon demo, clean theme](docs/hair-salon.png) |
| Frosted glass panels over a painted warm backdrop, serif headings | Dark, heavy uppercase type, the brand color as a bright accent | White and neutral, crisp lines, follows the visitor's light or dark setting |

## Make a mockup in 2 minutes

Windows (on macOS or Linux use `.venv/bin/` in place of `.venv\Scripts\`):

```
python -m venv .venv
.venv\Scripts\python -m pip install -e .
.venv\Scripts\sitegen new site.yml
```

Open `site.yml` and fill in the business: name, tagline, type, town, phone, address, hours, services and a brand color. Then:

```
.venv\Scripts\sitegen build site.yml -o out/ --theme warm
```

Open `out\index.html` in a browser. Try `--theme bold` and `--theme clean` to compare. Upload the `out` folder to any static host (GitHub Pages, Netlify, Cloudflare Pages) to publish it.

## The YAML file

```yaml
name: Hearth & Honey Bakery
tagline: Slow-fermented bread, flaky pastries and good coffee.
type: bakery                 # sets the schema.org type (Bakery, AutoRepair, HairSalon, ...)
town: Fernhaven
phone: (555) 014-2290
email: hello@example.com     # optional
address:
  street: 214 Orchard Lane
  region: ST                 # optional
  postal_code: "00000"       # optional
timezone: America/New_York   # optional, used by the "open now" badge
hours:                       # 9:00-17:00, 8am-2pm, "8:00-12:00, 13:00-17:00", 18:00-2:00, or closed
  mon: closed
  tue: 7:00-15:00
  sat: 7:30-14:00
services:                    # plain names, or name / price / description
  - name: Country sourdough
    price: 9
    description: Two-day ferment, crackly crust.
  - Celebration cakes
photos: []                   # none, or 3 to 6 file paths (copied next to the page) or https URLs
links:
  facebook: https://facebook.com/...
  google: https://g.page/...
  instagram: https://instagram.com/...
color: "#c2622d"             # text and button shades are adjusted to keep 4.5:1 contrast
theme: warm                  # warm, clean or bold
map: true                    # Google map embed of the address; false shows a link card instead
```

Days left out are shown as closed. Full examples: [examples/](examples).

Mistakes are reported all at once with the field name, for example:

```
error: site.yml has 2 problem(s):
  - `hours.tue`: 'nine' is not a time like 9:00, 17:30 or 5pm
  - `color` 'orange' must be a hex color like #b5523b
```

## What the page includes

- Semantic HTML with a skip link, landmarks and visible focus rings.
- Meta description, Open Graph tags and a LocalBusiness JSON-LD block (address, phone, opening hours, services, links).
- Google Fonts per theme, a generated favicon, no JavaScript framework. A small inline script marks today's row and shows "Open now, closes 5 PM" or "Closed, opens Tue 7 AM".
- Fade and slide-in on load and hover states, all CSS, switched off for visitors who ask for reduced motion.
- Layout tested at phone width (375px) and desktop.

## Development

```
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m mypy
.venv\Scripts\python -m pytest
.venv\Scripts\python scripts\build_demos.py   # builds the three demos into _site/
```

The `pages` workflow runs `scripts/build_demos.py` on every push to `main` and deploys `_site/` to GitHub Pages.

## License

MIT. Made by Chase Builds.
