import re
import unittest
from pathlib import Path

WORKFLOW = (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "nightly.yml").read_text()


def job_block(name):
    m = re.search(rf"^  {name}:\n((?:    .*\n|\n)+)", WORKFLOW, re.M)
    assert m, f"job {name} missing"
    return m.group(1)


class WorkflowTest(unittest.TestCase):
    def test_nightly_cron_and_manual_trigger(self):
        self.assertRegex(WORKFLOW, r"(?m)^on:\n(?:  .*\n)*?  schedule:\n    - cron: '[^']+'")
        self.assertIn("workflow_dispatch:", WORKFLOW)

    def test_build_runs_tests_then_build_and_uploads_pages_artifact(self):
        build = job_block("build")
        self.assertRegex(build, r"(?m)^      - run: python3 build\.py$")
        self.assertLess(build.index("unittest"), build.index("python3 build.py"))
        self.assertRegex(build, r"(?m)^      - uses: actions/upload-pages-artifact@")

    def test_deploy_needs_build_and_uses_deploy_pages(self):
        deploy = job_block("deploy")
        self.assertRegex(deploy, r"needs: build\b")
        self.assertRegex(deploy, r"(?m)^        uses: actions/deploy-pages@")

    def test_failures_are_not_swallowed(self):
        self.assertNotIn("continue-on-error", WORKFLOW)

    def test_pages_permissions(self):
        self.assertIn("pages: write", WORKFLOW)
        self.assertIn("id-token: write", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
