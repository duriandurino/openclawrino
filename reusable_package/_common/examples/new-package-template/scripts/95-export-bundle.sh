#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
# shellcheck source=/dev/null
source "$COMMON_DIR/scripts/common-export-helper.sh"

REPORTS_DIR="$ROOT_DIR/reports"
SLIDES_DIR="$ROOT_DIR/slides"
STAMP="$(common_export_stamp)"
PACKAGE_SLUG="new-package-template"
PANDOC_AVAILABLE=0

common_ensure_dir "$REPORTS_DIR"
common_ensure_dir "$SLIDES_DIR"

common_copy_stamped_file "$REPORTS_DIR/report.md" "$REPORTS_DIR" 'REPORT_FINAL' "$PACKAGE_SLUG" "$STAMP" >/dev/null
common_copy_stamped_file "$REPORTS_DIR/executive-summary.md" "$REPORTS_DIR" 'EXECUTIVE_SUMMARY' "$PACKAGE_SLUG" "$STAMP" >/dev/null
common_copy_stamped_file "$SLIDES_DIR/slides.md" "$SLIDES_DIR" 'SLIDES' "$PACKAGE_SLUG" "$STAMP" >/dev/null

if common_require_command pandoc; then
  PANDOC_AVAILABLE=1
  common_export_markdown_if_pandoc "$REPORTS_DIR/REPORT_FINAL_${PACKAGE_SLUG}_${STAMP}.md" "$REPORTS_DIR/REPORT_FINAL_${PACKAGE_SLUG}_${STAMP}.html" || true
  common_export_markdown_if_pandoc "$REPORTS_DIR/REPORT_FINAL_${PACKAGE_SLUG}_${STAMP}.md" "$REPORTS_DIR/REPORT_FINAL_${PACKAGE_SLUG}_${STAMP}.pdf" || true
fi

common_write_bundle_notes "$REPORTS_DIR/BUNDLE_NOTES_${STAMP}.md" "$PANDOC_AVAILABLE"
common_log_info 'Template export bundle complete.'
