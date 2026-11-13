import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.render import render_page
from src.stock import IN_STOCK, OUT_OF_STOCK, UNKNOWN, Retailer
from tests.check_page import TIME_FORMAT, check_page

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "fixtures" / "feeds"
NOW = datetime(2026, 11, 9, 2, 0, tzinfo=timezone.utc)
STAMP = NOW.strftime(TIME_FORMAT)
HOSTS = {"Shop": "shop.example.test"}


def page(**kw):
    base = dict(name="Shop", variant="256 GB", availability=IN_STOCK, order_url="https://shop.example.test/o", host="shop.example.test")
    base.update(kw)
    return render_page([Retailer(**base)], STAMP)


class CheckPageTest(unittest.TestCase):
    def test_good_page_passes(self):
        for status in (IN_STOCK, OUT_OF_STOCK, UNKNOWN):
            self.assertEqual(check_page(page(availability=status), HOSTS, NOW), [])

    def test_rejects_missing_status(self):
        self.assertTrue(check_page(page().replace("in stock", ""), HOSTS, NOW))

    def test_rejects_missing_link(self):
        self.assertTrue(check_page(page().replace('<a href="https://shop.example.test/o">Order</a>', ""), HOSTS, NOW))

    def test_rejects_off_domain_link(self):
        for url in ("https://evil.example.test/o", "http://shop.example.test/o", "https://shop.example.test.evil.test/o"):
            with self.subTest(url=url):
                self.assertTrue(check_page(page().replace("https://shop.example.test/o", url), HOSTS, NOW))

    def test_rejects_old_data(self):
        old = (NOW - timedelta(seconds=86401)).strftime(TIME_FORMAT)
        self.assertTrue(check_page(page().replace(STAMP, old), HOSTS, NOW))
        edge = (NOW - timedelta(seconds=86400)).strftime(TIME_FORMAT)
        self.assertEqual(check_page(page().replace(STAMP, edge), HOSTS, NOW), [])

    def test_rejects_missing_store_row(self):
        self.assertTrue(check_page(page(), {**HOSTS, "Other": "other.example.test"}, NOW))


class FeedFreshnessTest(unittest.TestCase):
    def test_future_as_of_beyond_clock_skew_is_not_fresh(self):
        from src.fetch import is_fresh
        for delta, fresh in ((timedelta(seconds=60), True), (timedelta(hours=1), False), (timedelta(hours=23), False), (-timedelta(seconds=86400), True), (-timedelta(seconds=86401), False)):
            with self.subTest(delta=delta):
                self.assertEqual(is_fresh(NOW + delta, NOW), fresh)


class BuiltPageTest(unittest.TestCase):
    def build(self, feeds):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = Path(tmp.name)
        retailers = [
            {"name": name, "host": "shop-a.example.test", "order_url": "https://shop-a.example.test/order/duo-256", "feed": feed if "://" in feed else (FEEDS / feed).as_uri()}
            for name, feed in feeds.items()
        ]
        (d / "cfg.json").write_text(json.dumps({"product": "iPhone Duo", "product_verified": False, "retailers": retailers}))
        r = subprocess.run([sys.executable, str(ROOT / "build.py"), "--config", str(d / "cfg.json"), "--site", str(d / "site")], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = (d / "site" / "index.html").read_text()
        hosts = {n: "shop-a.example.test" for n in feeds}
        self.assertEqual(check_page(html, hosts, datetime.now(timezone.utc)), [])
        return html

    def row(self, html, name):
        return html.split(f"<td>{name}</td>")[1].split("</tr>")[0]

    def test_unreadable_and_stale_feeds_render_unknown(self):
        html = self.build({
            "Good": "shop-a.json",
            "Malformed": "malformed.json",
            "Missing": "missing.json",
            "Unreachable": "http://127.0.0.1:9/feed.json",
            "Stale": "stale.json",
            "BadValue": "bad-availability.json",
        })
        self.assertIn("in stock", self.row(html, "Good"))
        for name in ("Malformed", "Missing", "Unreachable", "Stale", "BadValue"):
            with self.subTest(name=name):
                self.assertIn(">unknown<", self.row(html, name))
                self.assertNotIn("in stock", self.row(html, name))

    def test_fresh_as_of_is_shown_as_data_time(self):
        with tempfile.TemporaryDirectory() as t:
            as_of = datetime.now(timezone.utc) - timedelta(hours=3)
            feed = Path(t) / "f.json"
            feed.write_text(json.dumps({"as_of": as_of.isoformat(), "items": [{"variant": "v", "availability": "in_stock", "order_url": "https://shop-a.example.test/order/duo-256"}]}))
            row = self.row(self.build({"Fresh": feed.as_uri()}), "Fresh")
            self.assertIn(as_of.strftime(TIME_FORMAT), row)
            self.assertIn("in stock", row)


if __name__ == "__main__":
    unittest.main()
