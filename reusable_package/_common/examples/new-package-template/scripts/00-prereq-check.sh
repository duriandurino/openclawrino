#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
# shellcheck source=/dev/null
source "$COMMON_DIR/scripts/common-prereq-check.sh"

PACKAGE_OPTIONAL_TOOLS=(nmap ss ip)
COMMON_OPTIONAL_TOOLS+=("${PACKAGE_OPTIONAL_TOOLS[@]}")

common_run_prereq_check "$ROOT_DIR" "new-package-template" sha256sum
