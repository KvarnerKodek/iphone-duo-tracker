import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import build_site

DATA = json.loads((build_site.ROOT / "data" / "availability.json").read_text())


def build_with(data):
    with tempfile.TemporaryDirectory() as d:
        src, out = Path(d) / "a.json", Path(d) / "out" / "index.html"
        src.write_text(json.dumps(data))
        build_site.build(src, out)
        return out.read_text()


class PageTest(unittest.TestCase):
    def test_row_per_store_with_link_and_time(self):
        page = build_with(DATA)
        self.assertIn('lang="hr"', page)
        for s in DATA["stores"]:
            self.assertIn(f'data-store="{s["id"]}"', page)
            self.assertIn(f'href="{s["order_url"]}"', page)
        self.assertEqual(page.count("data-store="), len(DATA["stores"]))
        self.assertIn(f'<time datetime="{DATA["updated_at"]}">', page)

    def test_invalid_data_fails_build(self):
        def mutate(f):
            d = copy.deepcopy(DATA)
            f(d)
            return d
        cases = [
            mutate(lambda d: d.update(stores=[])),
            mutate(lambda d: d["stores"][0].pop("order_url")),
            mutate(lambda d: d["stores"][0].update(order_url="javascript:alert(1)")),
            mutate(lambda d: d.pop("updated_at")),
            mutate(lambda d: d.update(updated_at="yesterday")),
            mutate(lambda d: d["stores"][0].update(status="maybe")),
            mutate(lambda d: d["stores"][0].update(name="<script>x</script>")),
        ]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(build_site.BuildError):
                build_with(data)

    def test_values_escaped(self):
        d = copy.deepcopy(DATA)
        d["stores"][0]["name"] = 'A & "B"'
        page = build_with(d)
        self.assertIn("A &amp; &quot;B&quot;", page)


if __name__ == "__main__":
    unittest.main()
