import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "fixtures" / "feeds"


def entry(name, host, feed):
    return {"name": name, "host": host, "feed": feed if "://" in feed else (FEEDS / feed).as_uri()}


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
        self.assertNotIn("Shop B", html)

    def assert_failure_keeps_site(self, retailers):
        self.assertEqual(self.build([entry("Shop A", "shop-a.example.test", "shop-a.json")]).returncode, 0)
        before = self.index()
        r = self.build(retailers)
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr.strip())
        self.assertEqual(self.index(), before)
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["cfg.json", "site"])

    def test_one_of_several_failing_keeps_site(self):
        self.assert_failure_keeps_site([entry("Shop A", "shop-a.example.test", "shop-a.json"), entry("Gone", "gone.example.test", "missing.json")])

    def test_malformed_json_keeps_site(self):
        self.assert_failure_keeps_site([entry("Bad", "shop-a.example.test", "malformed.json")])

    def test_unknown_availability_keeps_site(self):
        self.assert_failure_keeps_site([entry("Bad", "shop-a.example.test", "bad-availability.json")])

    def test_off_host_link_keeps_site(self):
        self.assert_failure_keeps_site([entry("Shop A", "other.example.test", "shop-a.json")])

    def test_unreachable_http_feed_keeps_site(self):
        self.assert_failure_keeps_site([entry("Down", "shop-a.example.test", "http://127.0.0.1:9/feed.json")])

    def test_failure_without_prior_site_creates_none(self):
        self.assertNotEqual(self.build([entry("Gone", "gone.example.test", "missing.json")]).returncode, 0)
        self.assertFalse(self.site.exists())

    def test_repeated_runs_replace_site(self):
        self.build([entry("Shop A", "shop-a.example.test", "shop-a.json")])
        self.assertEqual(self.build([]).returncode, 0)
        self.assertIn(b"No retailers", self.index())


if __name__ == "__main__":
    unittest.main()
