import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "fixtures" / "feeds"
GOOD = {"name": "Shop A", "host": "shop-a.example.test", "feed": (FEEDS / "shop-a.json").as_uri()}


class FailsafeTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.index = self.dir / "site" / "index.html"

    def refresh(self, retailers):
        cfg = self.dir / "cfg.json"
        cfg.write_text(json.dumps({"product": "iPhone Duo", "product_verified": False, "retailers": retailers}))
        return subprocess.run(
            ["sh", str(ROOT / "refresh.sh"), str(cfg)],
            capture_output=True, text=True, cwd=ROOT, env={"PATH": "/usr/bin:/bin:/run/current-system/sw/bin", "SITE_DIR": str(self.dir / "site")},
        )

    def assert_keeps_page(self, bad):
        self.assertEqual(self.refresh([GOOD]).returncode, 0)
        before = self.index.read_bytes()
        r = self.refresh([GOOD, bad])
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.index.read_bytes(), before)

    def test_failsafe_malformed_feed_keeps_page(self):
        self.assert_keeps_page({"name": "Bad", "host": "bad.example.test", "feed": (FEEDS / "malformed.json").as_uri()})

    def test_failsafe_missing_feed_keeps_page(self):
        self.assert_keeps_page({"name": "Gone", "host": "gone.example.test", "feed": (FEEDS / "missing.json").as_uri()})

    def test_failsafe_failed_first_refresh_leaves_no_page(self):
        r = self.refresh([{"name": "Bad", "host": "bad.example.test", "feed": (FEEDS / "malformed.json").as_uri()}])
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.index.exists())
