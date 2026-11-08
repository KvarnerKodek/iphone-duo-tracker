import argparse
import fcntl
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from src.fetch import fetch_all
from src.render import render_page

ROOT = Path(__file__).resolve().parent


def replace_dir(new, target):
    old = target.with_name(target.name + ".old")
    if not target.exists() and old.exists():
        os.rename(old, target)
    shutil.rmtree(old, ignore_errors=True)
    if target.exists():
        os.rename(target, old)
    try:
        os.rename(new, target)
    except BaseException:
        if old.exists():
            os.rename(old, target)
        raise
    shutil.rmtree(old, ignore_errors=True)


def build(config_path, site):
    config = json.loads(Path(config_path).read_text())
    retailers = fetch_all(config["retailers"])
    refreshed = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = render_page(retailers, refreshed, config["product"], config["product_verified"])
    site.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=site.name + ".new.", dir=site.parent))
    try:
        (staging / "index.html").write_text(html, encoding="utf-8")
        fd = os.open(site.parent, os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            replace_dir(staging, site)
        finally:
            os.close(fd)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "retailers.json"))
    ap.add_argument("--site", default=str(ROOT / "site"))
    args = ap.parse_args(argv)
    try:
        build(args.config, Path(args.site))
    except Exception as e:
        print(f"build failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
