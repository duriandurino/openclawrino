#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${REUSABLE_COMMON_LIB_SH:-}" ]]; then
  return 0 2>/dev/null || exit 0
fi
readonly REUSABLE_COMMON_LIB_SH=1

common_timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

common_stamp_date() {
  date '+%Y-%m-%d'
}

common_stamp_datetime() {
  date '+%Y-%m-%d_%H%M%S'
}

common_log() {
  local level="$1"
  shift
  printf '[%s] [%s] %s\n' "$(common_timestamp)" "$level" "$*"
}

common_log_info() {
  common_log 'INFO' "$@"
}

common_log_warn() {
  common_log 'WARN' "$@"
}

common_log_error() {
  common_log 'ERROR' "$@" >&2
}

common_require_command() {
  local tool="$1"
  command -v "$tool" >/dev/null 2>&1
}

common_ensure_dir() {
  local dir="$1"
  mkdir -p "$dir"
}

common_hash_file() {
  local file="$1"
  if [[ ! -f "$file" ]]; then
    common_log_error "Cannot hash missing file: $file"
    return 1
  fi

  if common_require_command sha256sum; then
    sha256sum "$file"
  elif common_require_command shasum; then
    shasum -a 256 "$file"
  else
    common_log_error 'No supported hashing tool found (sha256sum or shasum).'
    return 1
  fi
}

common_copy_with_backup() {
  local source="$1"
  local destination="$2"

  if [[ ! -e "$source" ]]; then
    common_log_error "Source does not exist: $source"
    return 1
  fi

  local destination_dir
  destination_dir="$(dirname "$destination")"
  common_ensure_dir "$destination_dir"

  if [[ -e "$destination" ]]; then
    local backup_path="${destination}.bak.$(common_stamp_datetime)"
    cp -a "$destination" "$backup_path"
    common_log_info "Backed up existing file to $backup_path"
  fi

  cp -a "$source" "$destination"
  common_log_info "Copied $source -> $destination"
}

common_write_lines() {
  local output_file="$1"
  shift
  common_ensure_dir "$(dirname "$output_file")"
  printf '%s\n' "$@" > "$output_file"
}
