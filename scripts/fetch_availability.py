"""Fetch fresh availability data and replace data/availability.json only if it is valid."""
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path

from scripts import build_site

TARGET = build_site.ROOT / "data" / "availability.json"
TIMEOUT = 30


def _parse(ts):
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=build_site.UTC)


def check_against(current, new):
    build_site.validate(new)
    missing = {s["id"] for s in current["stores"]} - {s["id"] for s in new["stores"]}
    if missing:
        raise build_site.BuildError(f"tracked stores missing: {sorted(missing)}")
    if _parse(new["updated_at"]) < _parse(current["updated_at"]):
        raise build_site.BuildError("updated_at is older than the current data")


def main(url, target=TARGET):
    target = Path(target)
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            raw = resp.read()
        new = json.loads(raw)
        check_against(json.loads(target.read_text(encoding="utf-8")), new)
    except (OSError, ValueError, AttributeError, TypeError, build_site.BuildError) as err:
        print(f"fetch failed, data kept: {err}", file=sys.stderr)
        return 1
    fd, tmp = tempfile.mkstemp(dir=target.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(raw)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return 0


if __name__ == "__main__":
    url = os.environ.get("AVAILABILITY_URL")
    if not url:
        sys.exit("AVAILABILITY_URL is not set")
    sys.exit(main(url))
