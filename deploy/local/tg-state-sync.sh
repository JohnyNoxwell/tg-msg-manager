#!/bin/sh
set -eu

TGMM_SSH_HOST="${TGMM_SSH_HOST:-vps}"
TGMM_LOCAL_STATE_DIR="${TGMM_LOCAL_STATE_DIR:-$HOME/TG_MSG_MANAGER}"
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
  rsync -az --partial --info=progress2 "$@"
}

push_state() {
  mode=$1
  mkdir -p "$TGMM_LOCAL_STATE_DIR"
  if [ "$mode" = "--dry-run" ]; then
    run_rsync --dry-run "$TGMM_LOCAL_STATE_DIR/" "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/"
  elif [ "$mode" = "--apply" ]; then
    run_rsync "$TGMM_LOCAL_STATE_DIR/" "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/"
  else
    usage
    exit 2
  fi
}

pull_dir() {
  name=$1
  mkdir -p "$TGMM_LOCAL_STATE_DIR/$name"
  run_rsync "$TGMM_SSH_HOST:$TGMM_REMOTE_STATE_DIR/$name/" "$TGMM_LOCAL_STATE_DIR/$name/"
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
    pull_dir exports
    ;;
  pull:logs)
    pull_dir logs
    ;;
  pull:all)
    pull_dir exports
    pull_dir logs
    ;;
  *)
    usage
    exit 2
    ;;
esac
