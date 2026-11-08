import json
import unittest
from pathlib import Path

from src.render import render_page
from src.stock import IN_STOCK, OUT_OF_STOCK, UNKNOWN, Retailer, load_retailers

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "stock.json"
REFRESHED = "2026-11-08 02:00 UTC"


def retailer(**kw):
    base = dict(name="Shop", variant="256 GB", availability=IN_STOCK, order_url="https://shop.example.test/o", host="shop.example.test")
    base.update(kw)
    return Retailer(**base)


class RenderTest(unittest.TestCase):
    def test_lists_only_in_stock(self):
        html = render_page(load_retailers(FIXTURE), REFRESHED)
        self.assertIn("Fixture Shop Zagreb", html)
        self.assertIn("256 GB Black", html)
        self.assertIn("https://shop-a.example.test/order/duo-256", html)
        self.assertNotIn("Fixture Shop Split", html)

    def test_unknown_excluded(self):
        html = render_page(load_retailers(FIXTURE), REFRESHED)
        self.assertNotIn("Fixture Shop Rijeka", html)

    def test_refresh_time_shown_and_title_flags_unverified(self):
        self.assertIn(REFRESHED, render_page([], REFRESHED))
        def title(h):
            return h.split("<title>")[1].split("</title>")[0]
        self.assertNotEqual(title(render_page([], REFRESHED, verified=False)), title(render_page([], REFRESHED, verified=True)))

    def test_no_stock_shows_empty_state(self):
        html = render_page([retailer(availability=OUT_OF_STOCK), retailer(availability=UNKNOWN)], REFRESHED)
        self.assertIn("No retailers", html)
        self.assertNotIn("<li", html)

    def test_rejects_bad_links(self):
        for url in ("", "http://shop.example.test/o", "https://other.example.test/o", "javascript:alert(1)"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    render_page([retailer(order_url=url)], REFRESHED)

    def test_own_host_link_accepted(self):
        html = render_page([retailer()], REFRESHED)
        self.assertIn("https://shop.example.test/o", html)

    def test_bad_link_on_out_of_stock_ignored(self):
        html = render_page([retailer(availability=OUT_OF_STOCK, order_url="")], REFRESHED)
        self.assertNotIn("<li", html)

    def test_escapes_html(self):
        html = render_page([retailer(name="<script>x</script>", variant='"><b>')], REFRESHED)
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>", html)

    def test_loader_rejects_unknown_availability(self):
        with self.assertRaises(ValueError):
            Retailer.from_dict({"name": "a", "variant": "b", "availability": "maybe", "order_url": "", "host": "x"})


if __name__ == "__main__":
    unittest.main()
