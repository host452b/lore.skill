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
    r = run_validate(FIXTURES / "valid" / "2026-04-17-first-record.md")
    assert r.returncode == 0, r.stderr

def test_valid_full_passes():
    r = run_validate(FIXTURES / "valid" / "2026-04-17-adr-postgres-primary.md")
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


def test_tier_dir_mismatch_fails():
    r = run_validate(
        FIXTURES / "invalid" / "tier-dir-mismatch" / ".lore" / "live" / "journal"
        / "2026-04-17-labeled-canon.md"
    )
    assert r.returncode != 0
    assert "tier" in r.stderr.lower() or "directory" in r.stderr.lower()


def test_tier_check_skipped_outside_dot_lore():
    # The check only applies to files under a `.lore/<tier>/` layout.
    # A directory named 'canon' outside a .lore tree should not trigger
    # a false positive.
    r = run_validate(FIXTURES / "valid" / "canon" / "2026-04-17-should-pass.md")
    assert r.returncode == 0, r.stderr


def test_filename_id_mismatch_fails():
    r = run_validate(FIXTURES / "invalid" / "filename-id-mismatch.md")
    assert r.returncode != 0
    assert "filename" in r.stderr.lower() or "stem" in r.stderr.lower()


def test_bad_date_gives_clean_error_not_traceback():
    # Feb 30 is invalid; PyYAML raises ValueError. validate.py should
    # emit a clean ERROR message and exit non-zero without a Python traceback.
    r = run_validate(FIXTURES / "invalid" / "bad-date-feb-30.md")
    assert r.returncode != 0
    assert "Traceback" not in r.stderr
    assert "date" in r.stderr.lower() or "yaml" in r.stderr.lower()


def test_file_not_found_gives_clean_error():
    r = run_validate(FIXTURES / "does-not-exist.md")
    assert r.returncode != 0
    assert "Traceback" not in r.stderr
    assert "not found" in r.stderr.lower() or "no such" in r.stderr.lower()

def test_tfe_bad_status_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-bad-status-tfe.md")
    assert r.returncode != 0
    assert "status" in r.stderr.lower()

def test_tfe_unknown_profile_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-unknown-profile.md")
    assert r.returncode != 0
    assert "profile" in r.stderr.lower()
    assert "nonexistent" in r.stderr.lower() or "not found" in r.stderr.lower()

def test_tfe_missing_dont_retry_unless_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-missing-dru.md")
    assert r.returncode != 0
    assert "don't retry unless" in r.stderr.lower() or "retry" in r.stderr.lower()

def test_tfe_missing_what_was_chosen_instead_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-missing-chosen.md")
    assert r.returncode != 0
    assert "what was chosen instead" in r.stderr.lower() or "section" in r.stderr.lower()

def test_tfe_reassessed_without_superseded_by_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-reassessed-orphan.md")
    assert r.returncode != 0
    assert "superseded_by" in r.stderr.lower() or "reassessed" in r.stderr.lower()


def test_tfe_dont_retry_unless_inside_fence_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-dru-inside-fence.md")
    assert r.returncode != 0
    assert "don't retry unless" in r.stderr.lower() or "retry" in r.stderr.lower()
