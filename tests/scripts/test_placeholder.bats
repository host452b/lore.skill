# tests/scripts/test_placeholder.bats
@test "bats runner works" {
  result=$((1 + 1))
  [ "$result" -eq 2 ]
}
