setup() {
  export REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  export RUN_HOOK="$REPO_ROOT/hooks/run-hook.cmd"
}

@test "session-start emits Claude Code envelope when CLAUDE_PLUGIN_ROOT set" {
  CLAUDE_PLUGIN_ROOT="$REPO_ROOT" CURSOR_PLUGIN_ROOT="" COPILOT_CLI="" \
    run bash "$RUN_HOOK" session-start
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert 'hookSpecificOutput' in o, o
assert o['hookSpecificOutput']['hookEventName'] == 'SessionStart'
assert 'lore' in o['hookSpecificOutput']['additionalContext'].lower()
"
}

@test "session-start emits Cursor envelope when CURSOR_PLUGIN_ROOT set" {
  CLAUDE_PLUGIN_ROOT="" CURSOR_PLUGIN_ROOT="$REPO_ROOT" \
    run bash "$RUN_HOOK" session-start
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert 'additional_context' in o, o
assert 'lore' in o['additional_context'].lower()
"
}

@test "session-start emits SDK-standard envelope when no platform env set" {
  CLAUDE_PLUGIN_ROOT="" CURSOR_PLUGIN_ROOT="" COPILOT_CLI="1" \
    run bash "$RUN_HOOK" session-start
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert 'additionalContext' in o and 'hookSpecificOutput' not in o, o
"
}
