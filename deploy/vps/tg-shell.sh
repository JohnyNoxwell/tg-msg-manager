TGMM_ROOT="${TGMM_ROOT:-/opt/tg-msg-manager}"

tg() {
  "$TGMM_ROOT/deploy/vps/tgm" "$@"
}

tgd() {
  "$TGMM_ROOT/deploy/vps/tgm" clean --apply --yes "$@"
}

tge() {
  "$TGMM_ROOT/deploy/vps/tgm" export --deep --json --user-id "$@"
}

tgh() {
  "$TGMM_ROOT/deploy/vps/tgm" target names "$@"
}

tgpm() {
  "$TGMM_ROOT/deploy/vps/tgm" export-pm --user-id "$@"
}

tgr() {
  "$TGMM_ROOT/deploy/vps/tgm" clean --dry-run --yes "$@"
}

tgu() {
  "$TGMM_ROOT/deploy/vps/tgm" update "$@"
}
