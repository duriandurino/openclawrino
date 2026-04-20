#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../_common" && pwd)"

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo '[-] Run this installer with sudo or as root.' >&2
  exit 1
fi

echo '[+] Installing shared tools first'
bash "$COMMON_DIR/scripts/01-common-install.sh"

echo '[+] Installing Player V2 extra tools'
if command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get install -y iproute2 iputils-ping netcat-openbsd nmap systemd procps
elif command -v dnf >/dev/null 2>&1; then
  dnf install -y iproute iputils nmap nc systemd procps-ng
elif command -v pacman >/dev/null 2>&1; then
  pacman -Sy --noconfirm iproute2 iputils nmap gnu-netcat systemd procps-ng
else
  echo '[-] Unsupported package manager. Install Player V2 extra tools manually.' >&2
  exit 1
fi

echo '[+] Player V2 dependency install finished.'
echo "[+] You can now run: bash $ROOT_DIR/scripts/01-player-v2-setup.sh"
