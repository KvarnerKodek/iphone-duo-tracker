import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "fixtures" / "feeds"
GOOD = {"name": "Shop A", "host": "shop-a.example.test", "order_url": "https://shop-a.example.test/order/duo-256", "feed": (FEEDS / "shop-a.json").as_uri()}


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

    def test_failsafe_off_host_link_keeps_page(self):
        self.assert_keeps_page({**GOOD, "name": "Bad", "host": "other.example.test"})

    def test_failsafe_missing_config_key_keeps_page(self):
        self.assert_keeps_page({"name": "Bad", "host": "bad.example.test", "feed": GOOD["feed"]})

    def test_failsafe_failed_first_refresh_leaves_no_page(self):
        r = self.refresh([{**GOOD, "host": "other.example.test"}])
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.index.exists())

    def test_failsafe_unencodable_page_leaves_no_temp_file(self):
        cfg = self.dir / "stock.json"
        cfg.write_text(json.dumps({"retailers": [{"name": "\ud800", "variant": "256 GB", "availability": "in_stock", "order_url": "https://shop-a.example.test/o", "host": "shop-a.example.test"}]}))
        site = self.dir / "site"
        r = subprocess.run(["python3", "-m", "src", str(cfg), str(site)], capture_output=True, text=True, cwd=ROOT)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(list(site.iterdir()), [])
