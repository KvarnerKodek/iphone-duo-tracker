import json
import urllib.request
from datetime import datetime, timedelta, timezone

from .stock import UNKNOWN, Retailer

TIMEOUT_SECONDS = 10
MAX_DATA_AGE = timedelta(seconds=86400)
MAX_CLOCK_SKEW = timedelta(seconds=300)
TIME_FORMAT = "%Y-%m-%d %H:%M UTC"
DEFAULT_VARIANT = "iPhone Duo"


def read_url(url):
    with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
        return resp.read()


def is_fresh(as_of, now):
    return as_of.tzinfo is not None and -MAX_CLOCK_SKEW <= now - as_of <= MAX_DATA_AGE


def parse_feed(entry, raw, now):
    feed = json.loads(raw)
    extra = {}
    if feed.get("as_of") is not None:
        as_of = datetime.fromisoformat(feed["as_of"])
        if is_fresh(as_of, now):
            extra["data_time"] = as_of.astimezone(timezone.utc).strftime(TIME_FORMAT)
        else:
            extra["availability"] = UNKNOWN
    items = [
        Retailer.from_dict({
            "variant": item["variant"],
            "availability": item["availability"],
            "name": entry["name"],
            "host": entry["host"],
            "order_url": entry.get("order_url") or item["order_url"],
            **extra,
        })
        for item in feed["items"]
    ]
    if not items:
        raise ValueError("feed lists no items")
    return items


def unknown_retailer(entry):
    return Retailer(entry["name"], entry.get("variant", DEFAULT_VARIANT), UNKNOWN, entry["order_url"], entry["host"])


def fetch_retailer(entry, now):
    try:
        return parse_feed(entry, read_url(entry["feed"]), now)
    except Exception:
        return [unknown_retailer(entry)]


def fetch_all(entries, now=None):
    now = now or datetime.now(timezone.utc)
    names = [e["name"] for e in entries]
    if len(set(names)) != len(names):
        raise ValueError("duplicate retailer name in config")
    return [r for entry in entries for r in fetch_retailer(entry, now)]
