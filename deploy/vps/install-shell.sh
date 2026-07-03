#!/bin/sh
set -eu

BEGIN_MARKER="# >>> tg-msg-manager shell >>>"
END_MARKER="# <<< tg-msg-manager shell <<<"
SOURCE_LINE="source /opt/tg-msg-manager/deploy/vps/tg-shell.sh"

install_block() {
  rc_file=$1
  create_file=$2

  if [ "$create_file" = "yes" ] && [ ! -f "$rc_file" ]; then
    : > "$rc_file"
  elif [ ! -f "$rc_file" ]; then
    return 0
  fi

  if grep -Fqs "$BEGIN_MARKER" "$rc_file"; then
    return 0
  fi

  {
    printf '\n%s\n' "$BEGIN_MARKER"
    printf '%s\n' "$SOURCE_LINE"
    printf '%s\n' "$END_MARKER"
  } >> "$rc_file"
}

install_block "$HOME/.bashrc" yes
install_block "$HOME/.zshrc" no
