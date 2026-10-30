import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(*args, cwd=None):
    return subprocess.run(
        [sys.executable, *map(str, args)],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestScripts(unittest.TestCase):
    def test_index_demo_runs(self):
        # README: "python scripts/memory_index.py --demo" is the self-test
        result = run(SCRIPTS / "memory_index.py", "--demo")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_recall_demo_runs(self):
        result = run(SCRIPTS / "recall.py", "--demo")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ledger_demo_runs(self):
        result = run(SCRIPTS / "memory_ledger.py", "--demo")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_recall_with_nothing_to_search(self):
        # README: exit 3 = nothing could be searched at all.
        with tempfile.TemporaryDirectory() as tmp:
            result = run(SCRIPTS / "recall.py", "anything", "--paths", tmp, cwd=tmp)
            self.assertEqual(result.returncode, 3, result.stdout + result.stderr)

    def test_ledger_check_with_no_ledger(self):
        # Verified behaviour: no ledger yet is NOT an error — it returns 0
        # with a "no ledger yet" message. Do not assert non-zero here.
        with tempfile.TemporaryDirectory() as tmp:
            result = run(SCRIPTS / "memory_ledger.py", "--check", cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("no ledger yet", result.stdout + result.stderr)

    def test_ledger_check_reports_bad_ledger(self):
        # A ledger file that fails to load returns 2 (ledger error).
        with tempfile.TemporaryDirectory() as tmp:
            changsheng = Path(tmp) / ".changsheng"
            changsheng.mkdir()
            (changsheng / "ledger.json").write_text("{not json", encoding="utf-8")
            result = run(
                SCRIPTS / "memory_ledger.py", "--check",
                "--ledger", str(changsheng / "ledger.json"), cwd=tmp,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
