#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${1:-$ROOT_DIR/results/runs/$(date +%Y-%m-%d_%H%M%S)}"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$RUN_DIR" "$LOG_DIR"
STAMP="$(date +%Y-%m-%d_%H%M%S)"
OUT_SYS="$RUN_DIR/baseline-system.txt"
OUT_NET="$RUN_DIR/baseline-network.txt"
OUT_PROC="$RUN_DIR/baseline-processes.txt"
LOG_FILE="$LOG_DIR/live-baseline-$STAMP.log"
PATTERN='electron|python|node|phoenix|player|hardware|mqtt|nctv'

have_cmd() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n== %s ==\n' "$1"; }
run_or_note() {
  local label="$1"
  shift
  section "$label"
  if have_cmd "$1"; then
    "$@" 2>/dev/null || true
  else
    echo "command not found: $1"
  fi
}

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[+] Writing system baseline to $OUT_SYS"
{
  run_or_note "whoami" whoami
  run_or_note "date" date
  run_or_note "uname -a" uname -a
  section "/etc/os-release"
  cat /etc/os-release 2>/dev/null || echo "unavailable"
  run_or_note "hostnamectl" hostnamectl
  section "sudo -l"
  if have_cmd sudo; then
    sudo -n -l 2>/dev/null || sudo -l 2>/dev/null || echo "sudo -l unavailable or requires password"
  else
    echo "command not found: sudo"
  fi
  section "mounts"
  if have_cmd mount; then
    mount 2>/dev/null | sed -n '1,120p' || true
  else
    echo "command not found: mount"
  fi
} > "$OUT_SYS"

echo "[+] Writing network baseline to $OUT_NET"
{
  run_or_note "ip addr" ip addr
  run_or_note "ip route" ip route
  section "ss -tulpn"
  if have_cmd ss; then
    ss -tulpn 2>/dev/null || ss -tulpen 2>/dev/null || true
  else
    echo "command not found: ss"
  fi
} > "$OUT_NET"

echo "[+] Writing process baseline to $OUT_PROC"
{
  section "ps aux filtered"
  if have_cmd ps; then
    ps aux 2>/dev/null | grep -Ei "$PATTERN" | grep -v grep || true
  else
    echo "command not found: ps"
  fi
  section "systemctl units filtered"
  if have_cmd systemctl; then
    systemctl list-units --type=service --all 2>/dev/null | grep -Ei "$PATTERN" || true
  else
    echo "command not found: systemctl"
  fi
} > "$OUT_PROC"

echo "[+] Done. Baseline files written under $RUN_DIR"
