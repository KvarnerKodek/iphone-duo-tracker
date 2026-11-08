from html import escape
from urllib.parse import urlsplit

from .stock import IN_STOCK


def check_order_url(r):
    u = urlsplit(r.order_url)
    if any(c.isspace() for c in r.order_url) or u.scheme != "https" or not u.hostname or u.hostname != r.host.lower():
        raise ValueError(f"{r.name}: order link {r.order_url!r} is not an https link on {r.host}")


def render_page(retailers, refreshed, product="iPhone Duo", verified=False):
    listed = [r for r in retailers if r.availability == IN_STOCK]
    for r in listed:
        check_order_url(r)
    note = "" if verified else " (product name unverified)"
    items = "".join(
        f'<li><strong>{escape(r.name)}</strong> &mdash; {escape(r.variant)} &mdash; in stock '
        f'&mdash; <a href="{escape(r.order_url)}">Order</a></li>'
        for r in listed
    )
    body = f"<ul>{items}</ul>" if listed else "<p>No retailers currently have it in stock.</p>"
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{escape(product)}{escape(note)} stock in Croatia</title></head><body>"
        f"<h1>{escape(product)}{escape(note)} in stock in Croatia</h1>{body}"
        f"<p>Last refreshed: {escape(refreshed)}</p></body></html>\n"
    )
