from html import escape
from urllib.parse import urlsplit

from .stock import IN_STOCK, OUT_OF_STOCK, UNKNOWN


def check_order_url(r):
    u = urlsplit(r.order_url)
    if any(c.isspace() or c == "\\" for c in r.order_url) or u.username is not None or u.scheme != "https" or not u.hostname or u.hostname != r.host.lower():
        raise ValueError(f"{r.name}: order link {r.order_url!r} is not an https link on {r.host}")


STATUS_LABELS = {IN_STOCK: "in stock", OUT_OF_STOCK: "out of stock", UNKNOWN: "unknown"}


def render_page(retailers, refreshed, product="iPhone Duo", verified=False):
    for r in retailers:
        check_order_url(r)
    note = "" if verified else " (product name unverified)"
    rows = "".join(
        f"<tr><td>{escape(r.name)}</td><td>{escape(r.variant)}</td>"
        f'<td class="status">{STATUS_LABELS[r.availability]}</td>'
        f"<td>{escape(r.data_time or refreshed)}</td>"
        f'<td><a href="{escape(r.order_url)}">Order</a></td></tr>'
        for r in retailers
    )
    body = (
        "<table><thead><tr><th>Store</th><th>Variant</th><th>Status</th><th>Data time</th><th>Order</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
        if retailers else "<p>No retailers are configured.</p>"
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(product)}{escape(note)} stock in Croatia</title></head><body>"
        f"<h1>{escape(product)}{escape(note)} stock in Croatia</h1>{body}"
        f"<p>Last refreshed: {escape(refreshed)}</p></body></html>\n"
    )
