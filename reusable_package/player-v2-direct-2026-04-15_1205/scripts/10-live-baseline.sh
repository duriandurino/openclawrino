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

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[+] Writing system baseline to $OUT_SYS"
{
  echo "== whoami =="; whoami
  echo
  echo "== date =="; date
  echo
  echo "== uname -a =="; uname -a
  echo
  echo "== /etc/os-release =="; cat /etc/os-release 2>/dev/null || true
  echo
  echo "== hostnamectl =="; hostnamectl 2>/dev/null || true
  echo
  echo "== sudo -l =="; sudo -l 2>/dev/null || echo "sudo -l unavailable or requires password"
  echo
  echo "== mounts =="; mount | sed -n '1,120p'
} > "$OUT_SYS"

echo "[+] Writing network baseline to $OUT_NET"
{
  echo "== ip addr =="; ip addr
  echo
  echo "== ip route =="; ip route
  echo
  echo "== ss -tulpn =="; ss -tulpn 2>/dev/null || ss -tulpen 2>/dev/null || true
} > "$OUT_NET"

echo "[+] Writing process baseline to $OUT_PROC"
{
  echo "== ps aux filtered =="
  ps aux | grep -Ei 'electron|python|node|phoenix|player|hardware|mqtt|nctv' | grep -v grep || true
  echo
  echo "== systemctl units filtered =="
  systemctl list-units --type=service --all 2>/dev/null | grep -Ei 'electron|python|node|phoenix|player|hardware|mqtt|nctv' || true
} > "$OUT_PROC"

echo "[+] Done. Baseline files written under $RUN_DIR"