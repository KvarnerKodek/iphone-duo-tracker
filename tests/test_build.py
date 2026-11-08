import json
from datetime import datetime, timezone
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import build
from src.fetch import parse_feed

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "fixtures" / "feeds"


def entry(name, host, feed):
    return {"name": name, "host": host, "order_url": f"https://{host}/order/duo", "feed": feed if "://" in feed else (FEEDS / feed).as_uri()}


class BuildTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.site = self.dir / "site"

    def build(self, retailers, **extra):
        cfg = self.dir / "cfg.json"
        cfg.write_text(json.dumps({"product": "iPhone Duo", "product_verified": False, "retailers": retailers, **extra}))
        return subprocess.run(
            [sys.executable, str(ROOT / "build.py"), "--config", str(cfg), "--site", str(self.site)],
            capture_output=True, text=True, cwd=ROOT,
        )

    def index(self):
        return (self.site / "index.html").read_bytes()

    def test_shipped_config_builds_empty_state(self):
        r = subprocess.run([sys.executable, str(ROOT / "build.py"), "--site", str(self.site)], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = self.index().decode()
        self.assertIn("No retailers", html)
        self.assertIn("Last refreshed", html)
        self.assertIn("unverified", html)

    def test_lists_in_stock_from_feeds(self):
        r = self.build([entry("Shop A", "shop-a.example.test", "shop-a.json"), entry("Shop B", "shop-b.example.test", "shop-b.json")])
        self.assertEqual(r.returncode, 0, r.stderr)
        html = self.index().decode()
        self.assertIn("Shop A", html)
        self.assertIn("Shop B", html)
        self.assertIn("out of stock", html)

    def assert_failure_keeps_site(self, retailers):
        self.assertEqual(self.build([entry("Shop A", "shop-a.example.test", "shop-a.json")]).returncode, 0)
        before = self.index()
        r = self.build(retailers)
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr.strip())
        self.assertEqual(self.index(), before)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["cfg.json", "site"])

    def assert_unknown_row(self, name, feed):
        r = self.build([entry("Shop A", "shop-a.example.test", "shop-a.json"), entry(name, "bad.example.test", feed)])
        self.assertEqual(r.returncode, 0, r.stderr)
        row = self.index().decode().split(f"<td>{name}</td>")[1].split("</tr>")[0]
        self.assertIn(">unknown<", row)
        self.assertIn("https://bad.example.test/order/duo", row)

    def test_missing_feed_renders_unknown(self):
        self.assert_unknown_row("Gone", "missing.json")

    def test_malformed_json_renders_unknown(self):
        self.assert_unknown_row("Bad", "malformed.json")

    def test_unknown_availability_renders_unknown(self):
        self.assert_unknown_row("Bad", "bad-availability.json")

    def test_unreachable_http_feed_renders_unknown(self):
        self.assert_unknown_row("Down", "http://127.0.0.1:9/feed.json")

    def test_off_host_link_keeps_site(self):
        self.assert_failure_keeps_site([entry("Shop A", "other.example.test", "shop-a.json")])

    def test_failure_without_prior_site_creates_none(self):
        self.assertNotEqual(self.build([entry("Shop A", "other.example.test", "shop-a.json")]).returncode, 0)
        self.assertFalse(self.site.exists())

    def test_repeated_runs_replace_site(self):
        self.build([entry("Shop A", "shop-a.example.test", "shop-a.json")])
        self.assertEqual(self.build([]).returncode, 0)
        self.assertIn(b"No retailers", self.index())

    def test_failed_swap_after_interrupted_swap_restores_last_good_site(self):
        old = self.dir / "site.old"
        old.mkdir()
        (old / "index.html").write_text("last good")
        new = self.dir / "site.new"
        new.mkdir()
        real = build.os.rename

        def failing(src, dst):
            if Path(src) == new:
                raise OSError("boom")
            return real(src, dst)

        with mock.patch.object(build.os, "rename", failing):
            with self.assertRaises(OSError):
                build.replace_dir(new, self.site)
        self.assertEqual((self.site / "index.html").read_text(), "last good")

    def test_feed_item_cannot_override_configured_identity(self):
        raw = json.dumps({"items": [{"name": "Evil", "host": "evil.example.test", "variant": "v", "availability": "in_stock", "order_url": "https://a.example.test/o"}]})
        r = parse_feed({"name": "Shop", "host": "a.example.test"}, raw, datetime.now(timezone.utc))[0]
        self.assertEqual((r.name, r.host), ("Shop", "a.example.test"))


if __name__ == "__main__":
    unittest.main()
