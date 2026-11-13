import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

MAX_AGE = timedelta(seconds=86400)
MAX_CLOCK_SKEW = timedelta(seconds=300)
STATUSES = ("in stock", "out of stock", "unknown")
TIME_FORMAT = "%Y-%m-%d %H:%M UTC"


class Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.cell, self.in_body = [], None, False

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self.in_body = True
        elif tag == "tr" and self.in_body:
            self.rows.append({"cells": [], "href": None})
        elif tag == "td" and self.in_body:
            self.cell = []
            self.rows[-1]["cells"].append("")
        elif tag == "a" and self.rows and self.in_body:
            self.rows[-1]["href"] = dict(attrs).get("href")

    def handle_endtag(self, tag):
        if tag == "td" and self.cell is not None:
            self.rows[-1]["cells"][-1] = "".join(self.cell).strip()
            self.cell = None
        elif tag == "tbody":
            self.in_body = False

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)


def check_page(html, hosts, now):
    parser = Rows()
    parser.feed(html)
    problems = []
    seen = set()
    for row in parser.rows:
        cells = row["cells"]
        name = cells[0] if cells else ""
        if len(cells) < 5:
            problems.append(f"{name or 'row'}: row is missing cells")
            continue
        seen.add(name)
        if cells[2] not in STATUSES:
            problems.append(f"{name}: status {cells[2]!r} is not one of {STATUSES}")
        link = urlsplit(row["href"] or "")
        if not row["href"]:
            problems.append(f"{name}: no order link")
        elif link.scheme != "https" or link.hostname != hosts.get(name, "").lower():
            problems.append(f"{name}: order link {row['href']!r} is not an https link on {hosts.get(name)!r}")
        try:
            age = now - datetime.strptime(cells[3], TIME_FORMAT).replace(tzinfo=timezone.utc)
            if age > MAX_AGE:
                problems.append(f"{name}: data time {cells[3]!r} is older than {int(MAX_AGE.total_seconds())} s")
            elif age < -MAX_CLOCK_SKEW:
                problems.append(f"{name}: data time {cells[3]!r} is in the future")
        except ValueError:
            problems.append(f"{name}: data time {cells[3]!r} is not a time")
    for name in hosts:
        if name not in seen:
            problems.append(f"{name}: no row")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("--config", default="retailers.json")
    args = ap.parse_args(argv)
    hosts = {e["name"]: e["host"] for e in json.loads(Path(args.config).read_text())["retailers"]}
    problems = check_page(Path(args.page).read_text(encoding="utf-8"), hosts, datetime.now(timezone.utc))
    for p in problems:
        print(p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
