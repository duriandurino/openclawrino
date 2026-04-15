#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: bash scripts/90-export-md-to-html.sh <markdown-file>"
  exit 1
fi

INPUT="$1"
OUTPUT="${INPUT%.md}.html"

if command -v pandoc >/dev/null 2>&1; then
  pandoc "$INPUT" -o "$OUTPUT"
  echo "[+] Exported $OUTPUT"
else
  echo "[-] pandoc not found. Install pandoc or keep markdown as source of truth."
  exit 1
fi