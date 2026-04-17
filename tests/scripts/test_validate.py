# tests/scripts/test_validate.py
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATE = REPO_ROOT / "scripts" / "validate.py"
FIXTURES = Path(__file__).parent.parent / "fixtures"

def run_validate(path):
    return subprocess.run(
        ["python3", str(VALIDATE), str(path)],
        capture_output=True, text=True,
    )

def test_valid_minimal_passes():
    r = run_validate(FIXTURES / "valid" / "minimal.md")
    assert r.returncode == 0, r.stderr

def test_valid_full_passes():
    r = run_validate(FIXTURES / "valid" / "full.md")
    assert r.returncode == 0, r.stderr

def test_missing_id_fails():
    r = run_validate(FIXTURES / "invalid" / "missing-id.md")
    assert r.returncode != 0
    assert "id" in r.stderr.lower()

def test_bad_tier_fails():
    r = run_validate(FIXTURES / "invalid" / "bad-tier.md")
    assert r.returncode != 0
    assert "tier" in r.stderr.lower()

def test_bad_id_format_fails():
    r = run_validate(FIXTURES / "invalid" / "bad-id-format.md")
    assert r.returncode != 0
    assert "id" in r.stderr.lower()
