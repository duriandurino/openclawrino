#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo '[+] Running Player V2 package setup'
bash "$ROOT_DIR/scripts/00-prereq-check.sh"

echo
echo '[+] Next files to read:'
echo "    $ROOT_DIR/docs/operator-checklist.md"
echo "    $ROOT_DIR/docs/assessment-profile.md"
echo "    $ROOT_DIR/docs/handoff-notes.md"
echo
echo '[+] If the prereq check passed, you can continue with:'
echo "    bash $ROOT_DIR/scripts/00-bootstrap-engagement.sh"
