#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/20-network-check.sh <target-ip>"
  exit 1
fi

TARGET="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/results/runs/network-$(date +%Y-%m-%d_%H%M%S)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$RUN_DIR" "$LOG_DIR"
LOG_FILE="$LOG_DIR/network-check-$(date +%Y-%m-%d_%H%M%S).log"
PORTS=(22 80 111 443 1883 8883 3215 4200 5900 8080)

have_cmd() { command -v "$1" >/dev/null 2>&1; }

auto_probe() {
  local host="$1" port="$2"
  if have_cmd nc; then
    nc -vz -w 3 "$host" "$port" >/dev/null 2>&1 && echo "open-or-responding" || echo "closed-filtered-or-timeout"
  elif have_cmd timeout && have_cmd bash; then
    timeout 3 bash -lc "echo >/dev/tcp/$host/$port" >/dev/null 2>&1 && echo "open-or-responding" || echo "closed-filtered-or-timeout"
  else
    echo "probe-unavailable"
  fi
}

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[+] Quick reachability checks for $TARGET"
{
  echo "== ping =="
  if have_cmd ping; then
    ping -c 3 "$TARGET" || true
  else
    echo "command not found: ping"
  fi
  echo
  echo "== arp / neighbor =="
  if have_cmd ip; then
    ip neigh show | grep -F "$TARGET" || true
  elif have_cmd arp; then
    arp -an | grep -F "$TARGET" || true
  else
    echo "neighbor lookup unavailable"
  fi
  echo
  echo "== port spot checks =="
  for p in "${PORTS[@]}"; do
    echo "--- port $p ---"
    auto_probe "$TARGET" "$p"
  done
} | tee "$RUN_DIR/network-quick-check.txt"

if have_cmd nmap; then
  echo "[+] Running focused nmap"
  nmap -Pn -sS -sV -p "$(IFS=,; echo "${PORTS[*]}")" "$TARGET" -oN "$RUN_DIR/nmap-focused.txt" || true
else
  echo "[-] nmap not found, skipping focused scan"
fi

echo "[+] Done. Review $RUN_DIR for network notes."
