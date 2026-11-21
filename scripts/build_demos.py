"""Build the three demo sites plus an index page into _site/ (used by the Pages workflow)."""

from __future__ import annotations

import html
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from local_business_site.build import build  # noqa: E402
from local_business_site.config import load  # noqa: E402

DEMOS = ["bakery", "auto-repair", "hair-salon"]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>local-business-site demos</title>
<meta name="description" content="Three one-page websites for invented local businesses, each built
from one YAML file with local-business-site.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap">
<style>
*{{box-sizing:border-box}}
body{{margin:0;font-family:"Plus Jakarta Sans",system-ui,sans-serif;color:#2a1f1a;min-height:100vh;
background:radial-gradient(50% 45% at 10% 5%,rgba(240,150,100,.45),transparent 70%),
radial-gradient(45% 45% at 95% 20%,rgba(255,205,150,.7),transparent 70%),
radial-gradient(50% 50% at 70% 100%,rgba(240,160,170,.45),transparent 70%),#f7ece2}}
main{{max-width:1120px;margin:0 auto;padding:56px 16px}}
h1{{font-size:clamp(2rem,5vw,3.2rem);letter-spacing:-.03em;margin:0 0 10px}}
p.lead{{font-size:1.15rem;color:#5d4c42;max-width:60ch;margin:0 0 36px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:22px}}
a.card{{display:block;text-decoration:none;color:inherit;border-radius:22px;overflow:hidden;
background:rgba(255,250,245,.6);border:1px solid rgba(255,255,255,.8);
backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
box-shadow:0 18px 40px -20px rgba(90,50,30,.35);transition:transform .2s,box-shadow .2s}}
a.card:hover{{transform:translateY(-4px);box-shadow:0 26px 50px -20px rgba(90,50,30,.45)}}
a.card img{{display:block;width:100%;height:auto;aspect-ratio:16/10;object-fit:cover;object-position:top}}
.meta{{padding:16px 20px 20px}}
.meta strong{{font-size:1.15rem}}
.meta span{{display:block;color:#6b5a50;font-size:.95rem;margin-top:2px}}
footer{{margin-top:40px;color:#6b5a50;font-size:.92rem}}
footer a{{color:inherit}}
</style>
</head>
<body>
<main>
<h1>One YAML file, one polished page</h1>
<p class="lead">Three demo sites for invented local businesses. Each page was generated from a
single YAML file. Names, towns, addresses and 555 phone numbers are fictional.</p>
<div class="grid">
{cards}
</div>
<footer>Built with <a href="https://github.com/chasebuilds/local-business-site">local-business-site</a>
by Chase Builds.</footer>
</main>
</body>
</html>
"""


def main(out: Path = ROOT / "_site") -> None:
    if out.exists():
        shutil.rmtree(out)
    cards = []
    for name in DEMOS:
        site = load(ROOT / "examples" / f"{name}.yml")
        build(site, out / name)
        shot = ROOT / "docs" / f"{name}.png"
        if shot.exists():
            shutil.copyfile(shot, out / f"{name}.png")
        cards.append(
            f'<a class="card" href="{name}/"><img src="{name}.png" alt="{html.escape(site.name)}'
            f' demo screenshot" loading="lazy" width="1440" height="900"><div class="meta">'
            f"<strong>{html.escape(site.name)}</strong><span>{html.escape(site.type.capitalize())}"
            f", {site.theme} theme</span></div></a>"
        )
    (out / "index.html").write_text(PAGE.format(cards="\n".join(cards)), encoding="utf-8")
    print(f"built {len(DEMOS)} demos and index into {out}")


if __name__ == "__main__":
    main()
