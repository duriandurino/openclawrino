#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common-lib.sh"

COMMON_REQUIRED_TOOLS=(bash grep find sed awk python3)
COMMON_OPTIONAL_TOOLS=(pandoc)

common_run_prereq_check() {
  local package_root="$1"
  local package_name="$2"
  shift 2

  local -a extra_required=("$@")
  local -a required_tools=("${COMMON_REQUIRED_TOOLS[@]}" "${extra_required[@]}")
  local -a optional_tools=("${COMMON_OPTIONAL_TOOLS[@]}")

  local stamp log_dir out_dir out_file log_file missing_required
  stamp="$(common_stamp_datetime)"
  log_dir="$package_root/logs"
  out_dir="$package_root/results/prereq"
  out_file="$out_dir/prereq-check-$stamp.txt"
  log_file="$log_dir/prereq-check-$stamp.log"
  missing_required=0

  common_ensure_dir "$log_dir"
  common_ensure_dir "$out_dir"

  exec > >(tee -a "$log_file") 2>&1

  common_log_info "$package_name prerequisite check starting"
  common_log_info "Output file: $out_file"

  {
    echo "# Prerequisite Check"
    echo
    echo "Package: $package_name"
    echo "Generated: $(date)"
    echo
    echo "## Required tools"
    for tool in "${required_tools[@]}"; do
      if common_require_command "$tool"; then
        printf -- '- [OK] %s -> %s\n' "$tool" "$(command -v "$tool")"
      else
        printf -- '- [MISSING] %s\n' "$tool"
        missing_required=1
      fi
    done
    echo
    echo "## Optional tools"
    for tool in "${optional_tools[@]}"; do
      if common_require_command "$tool"; then
        printf -- '- [OK] %s -> %s\n' "$tool" "$(command -v "$tool")"
      else
        printf -- '- [MISSING] %s\n' "$tool"
      fi
    done
    echo
    echo "## Notes"
    echo '- Missing optional tools do not block the package, but they limit export or visibility features.'
    echo '- Extend this script in package-local wrappers when a package needs more tools.'
  } | tee "$out_file"

  if [[ "$missing_required" -eq 1 ]]; then
    common_log_error "Required tools are missing. Review $out_file before continuing."
    return 1
  fi

  common_log_info 'Prerequisite check complete.'
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <package-root> <package-name> [extra-required-tool ...]" >&2
    exit 1
  fi

  package_root="$1"
  package_name="$2"
  shift 2
  common_run_prereq_check "$package_root" "$package_name" "$@"
fi
