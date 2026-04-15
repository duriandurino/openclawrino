#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_TS="$(date +%Y-%m-%d_%H%M%S)"
RUN_DIR="$ROOT_DIR/results/runs/$RUN_TS"
LOG_DIR="$ROOT_DIR/logs"

mkdir -p "$RUN_DIR" "$LOG_DIR" "$ROOT_DIR/evidence" "$ROOT_DIR/results/normalized"

echo "[+] Created run directory: $RUN_DIR"
echo "[+] Created log directory: $LOG_DIR"

echo "run_timestamp=$RUN_TS" | tee "$RUN_DIR/run.meta"
echo "run_dir=$RUN_DIR" >> "$RUN_DIR/run.meta"
echo "package_root=$ROOT_DIR" >> "$RUN_DIR/run.meta"

cat <<EOF | tee "$LOG_DIR/bootstrap-$RUN_TS.log"
Player V2 reusable package bootstrap complete.
Run directory: $RUN_DIR
Next:
  1. Review docs/assessment-profile.md
  2. Run bash scripts/10-live-baseline.sh
  3. If needed, run bash scripts/20-network-check.sh <target-ip>
EOF
