import unittest

from src.fetch import fetch_all
from src.render import render_page
from src.stock import Retailer


def r(**kw):
    d = dict(name="A", variant="256 GB", availability="in_stock", order_url="https://a.example.test/o", host="a.example.test")
    return Retailer.from_dict({**d, **kw})


class HardeningTest(unittest.TestCase):
    def test_configured_host_case_is_ignored(self):
        render_page([r(host="A.Example.Test")], "now")

    def test_empty_variant_or_name_rejected(self):
        for kw in ({"variant": ""}, {"name": " "}):
            with self.assertRaises(ValueError):
                r(**kw)

    def test_whitespace_in_link_rejected(self):
        for u in (" https://a.example.test/o", "https://a.example.test/o\n", "https://evil.test\\@a.example.test/o", "https://evil.test@a.example.test/o"):
            with self.assertRaises(ValueError):
                render_page([r(order_url=u)], "now")

    def test_duplicate_retailer_names_rejected(self):
        e = {"name": "A", "host": "a.example.test", "feed": "file:///nonexistent"}
        with self.assertRaises(ValueError):
            fetch_all([e, e])


if __name__ == "__main__":
    unittest.main()
