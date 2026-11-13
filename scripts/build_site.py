"""Build the Croatian iPhone Duo stock page from data/availability.json."""
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

UTC = timezone.utc
ROOT = Path(__file__).resolve().parent.parent
STATUS_LABELS = {"in_stock": "Na zalihi", "out_of_stock": "Nema na zalihi", "unknown": "Nepoznato"}


class BuildError(Exception):
    pass


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"{field} missing or empty")
    return value


def validate(data):
    updated = _text(data.get("updated_at") if isinstance(data, dict) else None, "updated_at")
    try:
        datetime.fromisoformat(updated.replace("Z", "+00:00"))
    except ValueError:
        raise BuildError(f"updated_at is not an ISO timestamp: {updated!r}")
    stores = data.get("stores")
    if not isinstance(stores, list) or not stores:
        raise BuildError("stores is empty")
    ids = [s.get("id") if isinstance(s, dict) else None for s in stores]
    if len(set(ids)) != len(ids):
        raise BuildError("duplicate store ids")
    for s in stores:
        sid = _text(s.get("id"), "store id")
        name = _text(s.get("name"), f"{sid} name")
        if "<" in name or ">" in name:
            raise BuildError(f"{sid} name contains HTML")
        if s.get("status") not in STATUS_LABELS:
            raise BuildError(f"{sid} has invalid status {s.get('status')!r}")
        if not _text(s.get("order_url"), f"{sid} order_url").startswith(("https://", "http://")):
            raise BuildError(f"{sid} order_url is not an http(s) URL")


def render(data):
    validate(data)
    e = html.escape
    rows = "\n".join(
        f'      <tr data-store="{e(s["id"])}" data-status="{e(s["status"])}">'
        f'<td>{e(s["name"])}</td><td>{STATUS_LABELS[s["status"]]}</td>'
        f'<td><a href="{e(s["order_url"])}" rel="noopener">Naruči</a></td></tr>'
        for s in data["stores"]
    )
    ts = e(data["updated_at"])
    return f"""<!doctype html>
<html lang="hr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>iPhone Duo – dostupnost u Hrvatskoj</title>
</head>
<body>
  <h1>iPhone Duo – dostupnost u Hrvatskoj</h1>
  <p>Zadnje osvježeno: <time datetime="{ts}">{ts}</time></p>
  <table>
    <thead><tr><th>Trgovina</th><th>Dostupnost</th><th>Narudžba</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>
"""


def build(data_path=ROOT / "data" / "availability.json", out_path=ROOT / "site" / "index.html"):
    try:
        data = json.loads(Path(data_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise BuildError(f"cannot read {data_path}: {err}")
    page = render(data)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page, encoding="utf-8")


if __name__ == "__main__":
    try:
        build(*sys.argv[1:3])
    except BuildError as err:
        sys.exit(f"build failed: {err}")
