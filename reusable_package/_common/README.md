# Shared Common Layer

This `_common/` folder is the shared toolbox for reusable packages.

## Two simple shared scripts
Shared check script:
```bash
bash _common/scripts/00-common-setup.sh <package-root>
```

Shared install script:
```bash
sudo bash _common/scripts/01-common-install.sh
```

## What they do
- `00-common-setup.sh` = checks if the shared tools exist
- `01-common-install.sh` = installs the shared tools

## Shared tools this installer tries to install
- bash
- grep
- findutils
- sed
- awk / gawk
- python3
- coreutils
- pandoc

## Important note
The shared installer tries to support:
- `apt-get`
- `dnf`
- `pacman`

If your system uses something else, install the tools manually.

## Package-specific scripts
A target package can still have its own install script too.
For example, Player V2 adds:

```bash
sudo bash player-v2-direct-2026-04-15_1205/scripts/02-install-player-v2-tools.sh
```

That installs extra tools needed by that package.
