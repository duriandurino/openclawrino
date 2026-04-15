#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common-lib.sh"

common_export_stamp() {
  common_stamp_date
}

common_export_markdown_if_pandoc() {
  local source_md="$1"
  local output_path="$2"
  shift 2

  if ! common_require_command pandoc; then
    common_log_warn "pandoc not available, skipping export for $source_md -> $output_path"
    return 1
  fi

  pandoc "$source_md" -o "$output_path" "$@"
  common_log_info "Exported $source_md -> $output_path"
}

common_write_bundle_notes() {
  local notes_file="$1"
  local pandoc_available="$2"

  if [[ "$pandoc_available" == "1" ]]; then
    common_write_lines "$notes_file" \
      '# Bundle Notes' \
      '' \
      '- pandoc was available, so HTML/PDF/PPTX export was attempted.' \
      '- Review generated files and fix any local renderer issues if a specific export failed.'
  else
    common_write_lines "$notes_file" \
      '# Bundle Notes' \
      '' \
      '- pandoc was not available in this environment, so the bundle was generated as markdown-first deliverables only.' \
      '- Install pandoc to enable HTML/PDF/PPTX exports through this script.'
  fi

  common_log_info "Wrote bundle notes to $notes_file"
}

common_copy_stamped_file() {
  local source_file="$1"
  local destination_dir="$2"
  local prefix="$3"
  local suffix="$4"
  local stamp="${5:-$(common_export_stamp)}"
  local destination_file="$destination_dir/${prefix}_${suffix}_${stamp}.md"

  common_ensure_dir "$destination_dir"
  cp "$source_file" "$destination_file"
  common_log_info "Stamped file created: $destination_file"
  printf '%s\n' "$destination_file"
}
