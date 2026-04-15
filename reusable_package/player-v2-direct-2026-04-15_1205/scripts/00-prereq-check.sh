#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../_common" && pwd)"
# Optional shared layer path: reusable_package/_common/scripts/common-prereq-check.sh
# shellcheck source=/dev/null
source "$COMMON_DIR/scripts/common-prereq-check.sh"

PLAYER_V2_OPTIONAL_TOOLS=(ss ip systemctl nmap)
COMMON_OPTIONAL_TOOLS+=("${PLAYER_V2_OPTIONAL_TOOLS[@]}")

common_run_prereq_check "$ROOT_DIR" 'Player V2 package' sha256sum
