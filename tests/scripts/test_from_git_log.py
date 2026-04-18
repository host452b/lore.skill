import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent

# Load from-git-log.py as a module (hyphen in filename prevents normal import)
_spec = importlib.util.spec_from_file_location(
    "from_git_log",
    REPO_ROOT / "scripts" / "from-git-log.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

classify = _mod.classify
make_slug = _mod.make_slug
draft_journal = _mod.draft_journal
draft_tfe = _mod.draft_tfe


class TestClassify:
    def test_revert_is_tfe(self):
        assert classify({"is_revert": True, "subject": "Revert foo", "tags": []}) == "try-failed-exp"

    def test_deploy_subject_is_journal(self):
        assert classify({"is_revert": False, "subject": "deploy api v2", "tags": []}) == "journal"

    def test_release_tag_is_journal(self):
        assert classify({"is_revert": False, "subject": "merge PR #42", "tags": ["v1.3.0"]}) == "journal"

    def test_hotfix_subject_is_journal(self):
        assert classify({"is_revert": False, "subject": "hotfix: fix auth bug", "tags": []}) == "journal"

    def test_unrelated_commit_is_skipped(self):
        assert classify({"is_revert": False, "subject": "chore: update README", "tags": []}) is None

    def test_revert_takes_priority_over_deploy(self):
        assert classify({"is_revert": True, "subject": "Revert deploy api v2", "tags": []}) == "try-failed-exp"


class TestMakeSlug:
    def test_basic_slug(self):
        assert make_slug("deploy api v2") == "deploy-api-v2"

    def test_strips_revert_prefix(self):
        s = make_slug('Revert "redis cluster"')
        assert not s.startswith("revert")
        assert "redis" in s

    def test_truncates_long_slug(self):
        long = "a" * 60
        assert len(make_slug(long)) <= 50

    def test_no_leading_trailing_hyphens(self):
        s = make_slug("  deploy  ")
        assert not s.startswith("-")
        assert not s.endswith("-")


class TestDraftJournal:
    _event = {
        "sha": "abc1234567890",
        "subject": "deploy api v2",
        "author": "Joe",
        "email": "joe@example.com",
        "date": "2026-04-17T14:30:00+00:00",
        "is_revert": False,
        "is_merge": False,
        "tags": [],
    }

    def test_has_required_frontmatter_fields(self):
        content = draft_journal(self._event)
        for field in (
            "id:", "type: journal", "tier: live", "date:", "title:",
            "authors:", "profile: git-commit", "event-time:", "outcome: observed",
        ):
            assert field in content, f"missing: {field!r}"

    def test_id_starts_with_date(self):
        assert "id: 2026-04-17-" in draft_journal(self._event)

    def test_sha_in_body_comment(self):
        assert "abc1234567890"[:12] in draft_journal(self._event)

    def test_utc_offset_normalized_to_z(self):
        content = draft_journal(self._event)
        assert "+00:00" not in content
        assert "Z" in content


class TestDraftTfe:
    _event = {
        "sha": "def7890123456",
        "subject": 'Revert "redis cluster"',
        "author": "Joe",
        "email": "joe@example.com",
        "date": "2026-04-16T10:00:00+00:00",
        "is_revert": True,
        "is_merge": False,
        "tags": [],
    }

    def test_has_required_frontmatter_fields(self):
        content = draft_tfe(self._event)
        for field in (
            "id:", "type: try-failed-exp", "tier: canon", "date:", "title:",
            "authors:", "profile: revert-commit", "status: on-hold",
        ):
            assert field in content, f"missing: {field!r}"

    def test_has_required_body_sections(self):
        content = draft_tfe(self._event)
        assert "## What was reverted" in content
        assert "## Why reverted" in content
        assert "## Don't retry unless" in content


class TestCLI:
    def test_dry_run_exits_zero(self):
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "from-git-log.py"),
                "--dry-run",
                "--last", "3",
                "--repo", str(REPO_ROOT),
            ],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr

    def test_out_dir_created_when_not_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "staging"
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "from-git-log.py"),
                    "--out", str(out),
                    "--repo", str(REPO_ROOT),
                ],
                capture_output=True, text=True,
            )
            assert result.returncode == 0, result.stderr
            assert out.exists()
