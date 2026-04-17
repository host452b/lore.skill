# tests/scripts/test_new-id.bats
setup() {
  export REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  export NEW_ID="$REPO_ROOT/scripts/new-id.sh"
  export WORK="$(mktemp -d)"
}

teardown() {
  rm -rf "$WORK"
}

@test "generates YYYY-MM-DD-slug given date and slug" {
  run "$NEW_ID" --date 2026-04-17 --slug hello-world --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "2026-04-17-hello-world" ]
}

@test "uses today's date when --date omitted" {
  today=$(date +%Y-%m-%d)
  run "$NEW_ID" --slug hello --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "${today}-hello" ]
}

@test "appends -2 on collision with existing file" {
  touch "$WORK/2026-04-17-hello.md"
  run "$NEW_ID" --date 2026-04-17 --slug hello --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "2026-04-17-hello-2" ]
}

@test "appends -3 on double collision" {
  touch "$WORK/2026-04-17-hello.md" "$WORK/2026-04-17-hello-2.md"
  run "$NEW_ID" --date 2026-04-17 --slug hello --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "2026-04-17-hello-3" ]
}

@test "rejects uppercase slug" {
  run "$NEW_ID" --date 2026-04-17 --slug HELLO --dir "$WORK"
  [ "$status" -ne 0 ]
}

@test "rejects slug with spaces" {
  run "$NEW_ID" --date 2026-04-17 --slug "hello world" --dir "$WORK"
  [ "$status" -ne 0 ]
}

@test "rejects missing --slug" {
  run "$NEW_ID" --date 2026-04-17 --dir "$WORK"
  [ "$status" -ne 0 ]
}
