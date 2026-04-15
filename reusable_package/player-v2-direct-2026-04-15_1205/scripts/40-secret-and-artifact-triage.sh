#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/results/runs/secret-triage-$(date +%Y-%m-%d_%H%M%S)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$RUN_DIR" "$LOG_DIR"
LOG_FILE="$LOG_DIR/secret-triage-$(date +%Y-%m-%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "[+] Searching for likely secret and crypto workflow clues"
PATTERN='setup\.enc|vault\.img|openssl|cryptsetup|passphrase|serial|hardware_lock|phoenix|mqtt|token|secret|password'

{
  echo "== shell history candidates =="
  grep -RniE "$PATTERN" /home/pi/.*history /root/.*history 2>/dev/null || true
  echo
  echo "== app/config/script hits =="
  grep -RniE "$PATTERN" /opt /home/pi /etc 2>/dev/null | sed -n '1,400p' || true
  echo
  echo "== encrypted artifact candidates =="
  find /home/pi /opt -type f \( -name 'setup.enc' -o -name 'vault.img' -o -name '*.enc' -o -name '*.key' \) 2>/dev/null | sort || true
} > "$RUN_DIR/secret-triage.txt"

while IFS= read -r file; do
  [[ -f "$file" ]] || continue
  sha256sum "$file"
done < <(find /home/pi /opt -type f \( -name 'setup.enc' -o -name 'vault.img' -o -name '*.enc' \) 2>/dev/null | sort) > "$RUN_DIR/artifact-hashes.txt" || true

echo "[+] Secret triage complete. Review $RUN_DIR/secret-triage.txt and artifact-hashes.txt manually."