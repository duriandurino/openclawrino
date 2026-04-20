#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${1:-$(pwd)}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common-prereq-check.sh"

common_run_prereq_check "$ROOT_DIR" 'Reusable package common setup' sha256sum

echo
echo '[+] Common setup finished.'
echo '[+] This script checks whether the basic tools are present.'
echo '[+] It does not install packages automatically.'
