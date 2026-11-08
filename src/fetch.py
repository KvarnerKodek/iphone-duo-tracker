import json
import urllib.request

from .stock import Retailer

TIMEOUT_SECONDS = 10


def read_url(url):
    with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
        return resp.read()


def parse_feed(entry, raw):
    items = json.loads(raw)["items"]
    return [
        Retailer.from_dict({**item, "name": entry["name"], "host": entry["host"]})
        for item in items
    ]


def fetch_retailer(entry):
    url = entry["feed"]
    if not url.startswith(("http://", "https://", "file://")):
        raise ValueError(f"{entry['name']}: unsupported feed URL {url!r}")
    try:
        return parse_feed(entry, read_url(url))
    except Exception as e:
        raise RuntimeError(f"{entry['name']}: feed {url} failed: {e!r}") from e


def fetch_all(entries):
    names = [e["name"] for e in entries]
    if len(set(names)) != len(names):
        raise ValueError("duplicate retailer name in config")
    return [r for entry in entries for r in fetch_retailer(entry)]
