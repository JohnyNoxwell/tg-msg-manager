#!/bin/sh
set -eu

LOCK_FILE=/run/lock/tg-msg-manager-scheduler.lock
TGM=/opt/tg-msg-manager/deploy/vps/tgm

if [ "$#" -eq 0 ]; then
  printf '%s\n' "tg-msg-manager scheduler: missing CLI arguments" >&2
  exit 64
fi

exec 9>"$LOCK_FILE"

if ! flock -n 9; then
  printf '%s\n' "tg-msg-manager scheduler: another update or clean run is active; skipping: $*" >&2
  exit 75
fi

exec "$TGM" "$@"
