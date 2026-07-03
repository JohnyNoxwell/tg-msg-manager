#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
UNIT_SRC_DIR="$SCRIPT_DIR/systemd"
SYSTEMD_DIR=/etc/systemd/system

install -m 0644 "$UNIT_SRC_DIR/tg-msg-manager-update.service" "$SYSTEMD_DIR/tg-msg-manager-update.service"
install -m 0644 "$UNIT_SRC_DIR/tg-msg-manager-update.timer" "$SYSTEMD_DIR/tg-msg-manager-update.timer"
install -m 0644 "$UNIT_SRC_DIR/tg-msg-manager-clean.service" "$SYSTEMD_DIR/tg-msg-manager-clean.service"
install -m 0644 "$UNIT_SRC_DIR/tg-msg-manager-clean.timer" "$SYSTEMD_DIR/tg-msg-manager-clean.timer"

systemctl daemon-reload
systemctl enable --now tg-msg-manager-update.timer
systemctl enable --now tg-msg-manager-clean.timer

printf '%s\n' "Installed tg-msg-manager systemd timers."
printf '%s\n' ""
printf '%s\n' "Verification commands:"
printf '%s\n' "systemctl list-timers 'tg-msg-manager-*'"
printf '%s\n' "systemctl status tg-msg-manager-update.timer"
printf '%s\n' "systemctl status tg-msg-manager-clean.timer"
printf '%s\n' "journalctl -u tg-msg-manager-update.service"
printf '%s\n' "journalctl -u tg-msg-manager-clean.service"
