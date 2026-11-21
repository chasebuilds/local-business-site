"""Command line: ``sitegen build`` and ``sitegen new``."""

from __future__ import annotations

import argparse
import sys
from importlib import resources
from pathlib import Path

from . import __version__
from .build import build
from .config import THEMES, ConfigError, load


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sitegen", description="Turn one YAML file into a one-page local business website."
    )
    parser.add_argument("--version", action="version", version=f"sitegen {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="build index.html from a site YAML file")
    b.add_argument("config", type=Path, help="site YAML file")
    b.add_argument("-o", "--out", type=Path, default=Path("out"), help="output folder")
    b.add_argument("--theme", choices=THEMES, help="override the theme set in the file")

    n = sub.add_parser("new", help="write a starter site YAML file")
    n.add_argument("path", type=Path, nargs="?", default=Path("site.yml"))
    n.add_argument("--force", action="store_true", help="overwrite an existing file")

    args = parser.parse_args(argv)
    if args.command == "new":
        if args.path.exists() and not args.force:
            print(f"error: {args.path} already exists (use --force to overwrite)", file=sys.stderr)
            return 1
        starter = resources.files("local_business_site") / "starter.yml"
        args.path.write_text(starter.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"wrote {args.path}; edit it, then run: sitegen build {args.path} -o out/")
        return 0

    try:
        site = load(args.config)
        index = build(site, args.out, args.theme)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"built {index} ({args.theme or site.theme} theme)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
