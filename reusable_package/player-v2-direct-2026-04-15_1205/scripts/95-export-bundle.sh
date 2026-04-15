#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORTS_DIR="$ROOT_DIR/reports"
SLIDES_DIR="$ROOT_DIR/slides"
STAMP="$(date +%Y-%m-%d)"

mkdir -p "$REPORTS_DIR" "$SLIDES_DIR"

python3 "$ROOT_DIR/scripts/91-build-presentation-outline.py" "$REPORTS_DIR/findings.md" "$SLIDES_DIR/slides.md"

cp "$REPORTS_DIR/report.md" "$REPORTS_DIR/REPORT_FINAL_player-v2-direct_$STAMP.md"
cp "$REPORTS_DIR/executive-summary.md" "$REPORTS_DIR/EXECUTIVE_SUMMARY_player-v2-direct_$STAMP.md"
cp "$REPORTS_DIR/findings.md" "$REPORTS_DIR/FINDINGS_player-v2-direct_$STAMP.md"
cp "$REPORTS_DIR/remediation.md" "$REPORTS_DIR/REMEDIATION_player-v2-direct_$STAMP.md"
cp "$SLIDES_DIR/slides.md" "$SLIDES_DIR/SLIDES_player-v2-direct_$STAMP.md"

if command -v pandoc >/dev/null 2>&1; then
  pandoc "$REPORTS_DIR/REPORT_FINAL_player-v2-direct_$STAMP.md" -o "$REPORTS_DIR/REPORT_FINAL_player-v2-direct_$STAMP.html" || true
  pandoc "$REPORTS_DIR/REPORT_FINAL_player-v2-direct_$STAMP.md" -o "$REPORTS_DIR/REPORT_FINAL_player-v2-direct_$STAMP.pdf" || true
  pandoc "$SLIDES_DIR/SLIDES_player-v2-direct_$STAMP.md" -t pptx -o "$SLIDES_DIR/SLIDES_player-v2-direct_$STAMP.pptx" || true
  printf '%s\n' '# Bundle Notes' '' '- pandoc was available, so HTML/PDF/PPTX export was attempted.' '- Review generated files and fix any local renderer issues if a specific export failed.' > "$REPORTS_DIR/BUNDLE_NOTES_$STAMP.md"
else
  printf '%s\n' '# Bundle Notes' '' '- pandoc was not available in this environment, so the bundle was generated as markdown-first deliverables only.' '- Install pandoc to enable HTML/PDF/PPTX exports through this script.' > "$REPORTS_DIR/BUNDLE_NOTES_$STAMP.md"
fi

echo "[+] Export bundle complete. Review $REPORTS_DIR and $SLIDES_DIR"
