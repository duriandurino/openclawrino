#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y-%m-%d_%H%M%S)"
LOG_DIR="$ROOT_DIR/logs"
OUT_DIR="$ROOT_DIR/results/prereq"
OUT_FILE="$OUT_DIR/prereq-check-$STAMP.txt"
mkdir -p "$LOG_DIR" "$OUT_DIR"
exec > >(tee -a "$LOG_DIR/prereq-check-$STAMP.log") 2>&1

REQUIRED=(bash grep find sed awk sha256sum python3)
OPTIONAL=(ss ip systemctl nmap pandoc)
MISSING_REQUIRED=0

echo "[+] Player V2 package prerequisite check"
echo "[+] Output file: $OUT_FILE"
{
  echo "# Prerequisite Check"
  echo
  echo "Generated: $(date)"
  echo
  echo "## Required tools"
  for tool in "${REQUIRED[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
      printf -- "- [OK] %s -> %s\n" "$tool" "$(command -v "$tool")"
    else
      printf -- "- [MISSING] %s\n" "$tool"
      MISSING_REQUIRED=1
    fi
  done
  echo
  echo "## Optional tools"
  for tool in "${OPTIONAL[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
      printf -- "- [OK] %s -> %s\n" "$tool" "$(command -v "$tool")"
    else
      printf -- "- [MISSING] %s\n" "$tool"
    fi
  done
  echo
  echo "## Notes"
  echo "- Missing optional tools do not block the package, but they limit functionality."
  echo "- pandoc is only needed for PDF/PPTX style exports."
} | tee "$OUT_FILE"

if [[ "$MISSING_REQUIRED" -eq 1 ]]; then
  echo "[-] One or more required tools are missing. Review $OUT_FILE before continuing."
  exit 1
fi

echo "[+] Prerequisite check complete."
