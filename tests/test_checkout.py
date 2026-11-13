import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(os.environ.get("SITE_ROOT", ".")).resolve()
WORKFLOW = ROOT / ".github" / "workflows" / "refresh.yml"
GATE = "steps.fetch.outcome == 'success'"


def workflow_steps():
    text = WORKFLOW.read_text()
    return [s for s in re.split(r"\n      - ", text)[1:]]


class CheckoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "scripts/build_site.py"], cwd=ROOT, check=True)
        cls.page = (ROOT / "site" / "index.html").read_text()

    def test_row_per_tracked_store_with_status_link_and_time(self):
        import json
        stores = json.loads((ROOT / "data" / "availability.json").read_text())["stores"]
        self.assertGreater(len(stores), 0)
        rows = re.findall(r"<tr data-store=.*?</tr>", self.page, re.S)
        self.assertEqual(len(rows), len(stores))
        for store, row in zip(stores, rows):
            self.assertIn(f'data-store="{store["id"]}"', row)
            self.assertIn(f'data-status="{store["status"]}"', row)
            self.assertIn(f'href="{store["order_url"]}"', row)
        self.assertRegex(self.page, r"<time datetime=\"[^\"]+\">[^<]+</time>")

    def test_nightly_schedule_trigger(self):
        text = WORKFLOW.read_text()
        self.assertRegex(text, r"(?m)^on:\n(?:.*\n)*?  schedule:\n    - cron: \"[^\"]+\"")
        self.assertEqual(len(re.findall(r"- cron:", text)), 1)

    def test_every_publishing_step_is_gated_on_fetch_success(self):
        steps = workflow_steps()
        fetch = [s for s in steps if "id: fetch" in s]
        self.assertEqual(len(fetch), 1)
        self.assertNotIn(GATE, fetch[0])
        after = steps[steps.index(fetch[0]) + 1:]
        publishing = [s for s in after if re.search(r"build_site|configure-pages|upload-pages-artifact|deploy-pages", s)]
        self.assertGreaterEqual(len(publishing), 4)
        for step in publishing:
            self.assertIn(f"if: {GATE}", step)

    def test_pages_configuration(self):
        text = WORKFLOW.read_text()
        for needle in ("actions/configure-pages", "actions/upload-pages-artifact", "actions/deploy-pages",
                       "pages: write", "id-token: write"):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
