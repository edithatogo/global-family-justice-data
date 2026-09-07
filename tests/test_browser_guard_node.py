"""Run built-in-only Node guard tests; no browser or public network required."""

import shutil
import subprocess

import pytest


def test_node_browser_guards(project_root):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node runtime unavailable for optional browser inspection tooling")
    subprocess.run(
        [
            node,
            "--test",
            "scripts/g2_browser_egress.test.cjs",
            "scripts/g2_browser_policy.test.cjs",
            "scripts/g2_cdp_pipe.test.cjs",
        ],
        cwd=project_root,
        check=True,
        capture_output=True,
        timeout=30,
    )
