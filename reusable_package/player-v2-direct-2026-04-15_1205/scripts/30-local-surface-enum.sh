#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/results/runs/local-enum-$(date +%Y-%m-%d_%H%M%S)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$RUN_DIR" "$LOG_DIR"
LOG_FILE="$LOG_DIR/local-surface-enum-$(date +%Y-%m-%d_%H%M%S).log"
PATTERN='electron|player|phoenix|hardware|mqtt|python|node|nctv|pulse|setup\.enc|vault'
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[+] Enumerating likely app and service paths"

{
  echo "== candidate directories =="
  for path in /opt /home/pi /etc/systemd/system /lib/systemd/system; do
    [[ -e "$path" ]] && echo "$path"
  done
  echo
  echo "== /opt listing =="
  [[ -d /opt ]] && find /opt -maxdepth 3 -type f 2>/dev/null | grep -Ei "$PATTERN" | sort || true
  echo
  echo "== /home/pi listing =="
  [[ -d /home/pi ]] && find /home/pi -maxdepth 4 -type f 2>/dev/null | grep -Ei "$PATTERN" | sort || true
  echo
  echo "== systemd unit references =="
  grep -RniE 'electron|player|phoenix|hardware|mqtt|nctv|pulse' /etc/systemd/system /lib/systemd/system 2>/dev/null || true
} > "$RUN_DIR/local-surface.txt"

echo "[+] Local surface inventory written to $RUN_DIR/local-surface.txt"
