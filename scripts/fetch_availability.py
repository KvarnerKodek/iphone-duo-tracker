"""Fetch fresh availability data and replace data/availability.json only if it is valid."""
import json
import os
import sys
import tempfile
import urllib.request
import time
from datetime import datetime, timedelta
from pathlib import Path

from scripts import build_site

TARGET = build_site.ROOT / "data" / "availability.json"
TIMEOUT = 30
DEADLINE = 60
MAX_BYTES = 1 << 20
FUTURE_SLACK = timedelta(days=1)


def _parse(ts):
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=build_site.UTC)


def _read(resp):
    end = time.monotonic() + DEADLINE
    raw = b""
    while chunk := resp.read1(65536):
        raw += chunk
        if len(raw) > MAX_BYTES:
            raise build_site.BuildError("response too large")
        if time.monotonic() > end:
            raise build_site.BuildError("response too slow")
    return raw


def _baseline(target):
    try:
        current = json.loads(Path(target).read_text(encoding="utf-8"))
        build_site.validate(current)
    except (OSError, ValueError, AttributeError, TypeError, build_site.BuildError):
        return None
    return current


def check_against(current, new):
    build_site.validate(new)
    if _parse(new["updated_at"]) > datetime.now(build_site.UTC) + FUTURE_SLACK:
        raise build_site.BuildError("updated_at is in the future")
    if current is None:
        return
    missing = {s["id"] for s in current["stores"]} - {s["id"] for s in new["stores"]}
    if missing:
        raise build_site.BuildError(f"tracked stores missing: {sorted(missing)}")
    if _parse(new["updated_at"]) < _parse(current["updated_at"]):
        raise build_site.BuildError("updated_at is older than the current data")


def main(url, target=TARGET):
    target = Path(target)
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            raw = _read(resp)
        new = json.loads(raw)
        check_against(_baseline(target), new)
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
