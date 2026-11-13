import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

CONFIG = json.loads((Path(__file__).resolve().parent.parent / "retailers.json").read_text())


class ConfigTest(unittest.TestCase):
    def test_has_stores(self):
        self.assertTrue(CONFIG["retailers"])

    def test_names_unique(self):
        names = [r["name"] for r in CONFIG["retailers"]]
        self.assertEqual(len(names), len(set(names)))

    def test_order_urls_are_https_on_own_host(self):
        for r in CONFIG["retailers"]:
            with self.subTest(store=r["name"]):
                u = urlsplit(r["order_url"])
                self.assertEqual(u.scheme, "https")
                self.assertTrue(u.hostname)
                self.assertEqual(u.hostname, r["host"].lower())
                self.assertIsNone(u.username)

    def test_feeds_are_http_or_file_urls(self):
        for r in CONFIG["retailers"]:
            with self.subTest(store=r["name"]):
                self.assertTrue(r["feed"].startswith(("https://", "http://", "file://")))


if __name__ == "__main__":
    unittest.main()
