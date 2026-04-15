#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$ROOT_DIR/results/runs/secret-triage-$(date +%Y-%m-%d_%H%M%S)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$RUN_DIR" "$LOG_DIR"
LOG_FILE="$LOG_DIR/secret-triage-$(date +%Y-%m-%d_%H%M%S).log"
PATTERN='setup\.enc|vault\.img|openssl|cryptsetup|passphrase|serial|hardware_lock|phoenix|mqtt|token|secret|password'
SEARCH_PATHS=(/opt /home/pi /etc)
ARTIFACT_PATHS=(/home/pi /opt)

exec > >(tee -a "$LOG_FILE") 2>&1

echo "[+] Searching for likely secret and crypto workflow clues"

{
  echo "== shell history candidates =="
  grep -RniE "$PATTERN" /home/pi/.*history /root/.*history 2>/dev/null || true
  echo
  echo "== app/config/script hits =="
  grep -RniE "$PATTERN" "${SEARCH_PATHS[@]}" 2>/dev/null | sed -n '1,400p' || true
  echo
  echo "== encrypted artifact candidates =="
  find "${ARTIFACT_PATHS[@]}" -type f \( -name 'setup.enc' -o -name 'vault.img' -o -name '*.enc' -o -name '*.key' \) 2>/dev/null | sort || true
} > "$RUN_DIR/secret-triage.txt"

if command -v sha256sum >/dev/null 2>&1; then
  while IFS= read -r file; do
    [[ -f "$file" ]] || continue
    sha256sum "$file"
  done < <(find "${ARTIFACT_PATHS[@]}" -type f \( -name 'setup.enc' -o -name 'vault.img' -o -name '*.enc' \) 2>/dev/null | sort) > "$RUN_DIR/artifact-hashes.txt" || true
else
  echo "sha256sum not found" > "$RUN_DIR/artifact-hashes.txt"
fi

echo "[+] Secret triage complete. Review $RUN_DIR/secret-triage.txt and artifact-hashes.txt manually."
