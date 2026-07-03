#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEFAULT_LOCAL_STATE_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)

TGMM_SSH_HOST="${TGMM_SSH_HOST:-vps}"
TGMM_LOCAL_STATE_DIR="${TGMM_LOCAL_STATE_DIR:-$DEFAULT_LOCAL_STATE_DIR}"
TGMM_REMOTE_STATE_DIR="${TGMM_REMOTE_STATE_DIR:-/opt/tg-msg-manager/state}"

usage() {
  printf '%s\n' "Usage:"
  printf '%s\n' "  $0 push --dry-run"
  printf '%s\n' "  $0 push --apply"
  printf '%s\n' "  $0 pull exports"
  printf '%s\n' "  $0 pull logs"
  printf '%s\n' "  $0 pull all"
}

run_rsync() {
  rsync -azr --partial --info=progress2 "$@"
}

remote_shell_quote() {
  printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

warn_if_locked() {
  if [ -e "$TGMM_LOCAL_STATE_DIR/.tg_msg_manager.lock" ]; then
    printf '%s\n' "WARNING: local .tg_msg_manager.lock exists; stop tg-msg-manager before push. Lock file will not be synced." >&2
  fi
}

append_existing_path() {
  files_from=$1
  relative_path=$2

  if [ -e "$TGMM_LOCAL_STATE_DIR/$relative_path" ]; then
    printf '%s\0' "$relative_path" >> "$files_from"
  fi
}

append_root_matches() {
  files_from=$1
  pattern=$2

  find "$TGMM_LOCAL_STATE_DIR" -maxdepth 1 -name "$pattern" -exec sh -c '
    files_from=$1
    shift
    for path do
      relative_path=${path##*/}
      printf "%s\0" "$relative_path" >> "$files_from"
    done
  ' sh "$files_from" {} +
}

build_push_file_list() {
  files_from=$1

  append_existing_path "$files_from" config.json
  append_existing_path "$files_from" config.local.json
  append_existing_path "$files_from" DB_TARGETS.txt
  append_existing_path "$files_from" delete_log.txt
  append_existing_path "$files_from" export_state.json
  append_existing_path "$files_from" deep_export_state.json
  append_existing_path "$files_from" deep_json_export_state.json
  append_existing_path "$files_from" json_export_state.json
  append_existing_path "$files_from" pm_export_state.json

  append_root_matches "$files_from" "*.log"
  append_root_matches "$files_from" "*.session"
  append_root_matches "$files_from" "*.session-shm"
  append_root_matches "$files_from" "*.session-wal"
  append_root_matches "$files_from" "*.session-journal"
  append_root_matches "$files_from" "*.db"
  append_root_matches "$files_from" "*.db-shm"
  append_root_matches "$files_from" "*.db-wal"
  append_root_matches "$files_from" "*.db-journal"
  append_root_matches "$files_from" "*.sqlite"
  append_root_matches "$files_from" "*.sqlite-shm"
  append_root_matches "$files_from" "*.sqlite-wal"
  append_root_matches "$files_from" "*.sqlite-journal"
  append_root_matches "$files_from" "*.sqlite3"
  append_root_matches "$files_from" "*.sqlite3-shm"
  append_root_matches "$files_from" "*.sqlite3-wal"
  append_root_matches "$files_from" "*.sqlite3-journal"

  append_existing_path "$files_from" DB_EXPORTS/
  append_existing_path "$files_from" PUBLIC_GROUPS/
  append_existing_path "$files_from" PRIVAT_DIALOGS/
  append_existing_path "$files_from" exports/
  append_existing_path "$files_from" LOGS/
}

push_state() {
  mode=$1
  files_from=$(mktemp)
  trap 'rm -f "$files_from"' EXIT HUP INT TERM

  warn_if_locked
  build_push_file_list "$files_from"

  if [ "$mode" = "--dry-run" ]; then
    run_rsync --dry-run --from0 --files-from="$files_from" "$TGMM_LOCAL_STATE_DIR/" "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/"
  elif [ "$mode" = "--apply" ]; then
    quoted_remote_dir=$(remote_shell_quote "$TGMM_REMOTE_STATE_DIR")
    ssh "$TGMM_SSH_HOST" "mkdir -p $quoted_remote_dir"
    run_rsync --from0 --files-from="$files_from" "$TGMM_LOCAL_STATE_DIR/" "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/"
  else
    usage
    exit 2
  fi
}

remote_path_exists() {
  relative_path=$1
  quoted_remote_path=$(remote_shell_quote "$TGMM_REMOTE_STATE_DIR/$relative_path")
  ssh "$TGMM_SSH_HOST" "test -e $quoted_remote_path"
}

remote_root_logs_exist() {
  quoted_remote_dir=$(remote_shell_quote "$TGMM_REMOTE_STATE_DIR")
  ssh "$TGMM_SSH_HOST" "set -- $quoted_remote_dir/*.log; [ -e \"\$1\" ]"
}

pull_optional_dir() {
  name=$1
  if remote_path_exists "$name"; then
    mkdir -p "$TGMM_LOCAL_STATE_DIR/$name"
    run_rsync "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/$name/" "$TGMM_LOCAL_STATE_DIR/$name/"
  else
    printf '%s\n' "skip missing remote path: $name" >&2
  fi
}

pull_optional_file() {
  name=$1
  if remote_path_exists "$name"; then
    mkdir -p "$TGMM_LOCAL_STATE_DIR"
    run_rsync "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/$name" "$TGMM_LOCAL_STATE_DIR/"
  else
    printf '%s\n' "skip missing remote path: $name" >&2
  fi
}

pull_root_logs() {
  if remote_root_logs_exist; then
    mkdir -p "$TGMM_LOCAL_STATE_DIR"
    run_rsync "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/"*.log "$TGMM_LOCAL_STATE_DIR/"
  else
    printf '%s\n' "skip missing remote path: *.log" >&2
  fi
}

pull_exports() {
  pull_optional_dir exports
  pull_optional_dir DB_EXPORTS
  pull_optional_dir PUBLIC_GROUPS
  pull_optional_dir PRIVAT_DIALOGS
}

pull_logs() {
  pull_optional_dir LOGS
  pull_optional_file delete_log.txt
  pull_root_logs
}

if [ "$#" -lt 2 ]; then
  usage
  exit 2
fi

case "$1:$2" in
  push:--dry-run | push:--apply)
    push_state "$2"
    ;;
  pull:exports)
    pull_exports
    ;;
  pull:logs)
    pull_logs
    ;;
  pull:all)
    pull_exports
    pull_logs
    ;;
  *)
    usage
    exit 2
    ;;
esac
