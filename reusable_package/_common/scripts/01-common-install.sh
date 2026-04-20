#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common-lib.sh"

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  common_log_error 'Run this installer with sudo or as root.'
  exit 1
fi

install_with_apt() {
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y bash grep findutils sed gawk python3 coreutils pandoc
}

install_with_dnf() {
  dnf install -y bash grep findutils sed gawk python3 coreutils pandoc
}

install_with_pacman() {
  pacman -Sy --noconfirm bash grep findutils sed gawk python python-pip pandoc coreutils
}

common_log_info 'Starting shared dependency install'

if common_require_command apt-get; then
  install_with_apt
elif common_require_command dnf; then
  install_with_dnf
elif common_require_command pacman; then
  install_with_pacman
else
  common_log_error 'Unsupported package manager. Install the required tools manually.'
  exit 1
fi

common_log_info 'Shared dependency install finished.'
