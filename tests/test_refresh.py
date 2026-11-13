import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "fixtures" / "feeds"


class RefreshTest(unittest.TestCase):
    def run_refresh(self, retailers):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        d = Path(tmp.name)
        cfg = d / "cfg.json"
        cfg.write_text(json.dumps({"product": "iPhone Duo", "product_verified": False, "retailers": retailers}))
        r = subprocess.run(
            ["sh", str(ROOT / "refresh.sh"), str(cfg)],
            capture_output=True, text=True, cwd=ROOT, env={"PATH": "/usr/bin:/bin:/run/current-system/sw/bin", "SITE_DIR": str(d / "site")},
        )
        return r, d / "site" / "index.html"

    def test_refresh_lists_in_stock_shop_with_order_link(self):
        r, index = self.run_refresh([{"name": "Shop A", "host": "shop-a.example.test", "order_url": "https://shop-a.example.test/order/duo-256", "feed": (FEEDS / "shop-a.json").as_uri()}])
        self.assertEqual(r.returncode, 0, r.stderr)
        html = index.read_text()
        self.assertIn("Shop A", html)
        self.assertIn('href="https://shop-a.example.test/order/duo-256"', html)
        self.assertIn("Last refreshed", html)
