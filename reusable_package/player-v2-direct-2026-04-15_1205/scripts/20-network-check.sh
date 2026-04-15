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
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[+] Quick reachability checks for $TARGET"
{
  echo "== ping =="; ping -c 3 "$TARGET" || true
  echo
  echo "== arp =="; ip neigh show | grep "$TARGET" || true
  echo
  echo "== nc spot checks =="
  for p in 22 80 111 443 1883 8883 3215 4200 5900 8080; do
    echo "--- port $p ---"
    timeout 3 bash -lc "echo >/dev/tcp/$TARGET/$p" && echo "open-or-responding" || echo "closed-filtered-or-timeout"
  done
} | tee "$RUN_DIR/network-quick-check.txt"

if command -v nmap >/dev/null 2>&1; then
  echo "[+] Running focused nmap"
  nmap -Pn -sS -sV -p 22,80,111,443,1883,8883,3215,4200,5900,8080 "$TARGET" -oN "$RUN_DIR/nmap-focused.txt" || true
else
  echo "[-] nmap not found, skipping focused scan"
fi

echo "[+] Done. Review $RUN_DIR for network notes."