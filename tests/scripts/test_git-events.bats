# tests/scripts/test_git-events.bats
setup() {
  export REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  export GIT_EVENTS="$REPO_ROOT/scripts/git-events.sh"
  export WORK="$(mktemp -d)"

  # Build a tiny throwaway repo with deterministic commits
  cd "$WORK"
  git init -q -b main
  git config user.email "test@example.com"
  git config user.name "Test"
  echo a > a.txt && git add a.txt && git commit -qm "first commit"
  echo b > b.txt && git add b.txt && git commit -qm "second commit"
  echo c > a.txt && git add a.txt && git commit -qm "Revert \"first commit\""
}

teardown() {
  rm -rf "$WORK"
}

@test "emits one JSON line per commit" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  count=$(printf '%s\n' "$output" | grep -c '^{')
  [ "$count" -eq 3 ]
}

@test "each JSON line has sha, subject, author, date fields" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  echo "$output" | head -n1 | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
for f in ('sha', 'subject', 'author', 'date'):
    assert f in o, f'{f} missing from: {o}'
"
}

@test "marks revert commits with is_revert: true" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  revert_line=$(printf '%s\n' "$output" | grep -E 'Revert' || true)
  [ -n "$revert_line" ]
  echo "$revert_line" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert o.get('is_revert') is True, o
"
}

@test "non-revert commits have is_revert: false" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  first_non_revert=$(printf '%s\n' "$output" | grep -vE 'Revert' | head -n1)
  echo "$first_non_revert" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert o.get('is_revert') is False, o
"
}

@test "respects --since argument" {
  cd "$WORK"
  run bash "$GIT_EVENTS" --since "1 year ago"
  [ "$status" -eq 0 ]
  count=$(printf '%s\n' "$output" | grep -c '^{')
  [ "$count" -eq 3 ]
}
