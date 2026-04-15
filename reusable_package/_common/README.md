# Reusable Package Common Layer

This `_common/` directory is the shared foundation for reusable pentest package folders under `reusable_package/`.

It gives package authors a small, consistent base for:
- prerequisite checking
- export helper flows
- shared shell utility functions
- package bootstrap examples
- docs for turning a package into its own git repository

## Layout

- `scripts/common-lib.sh` - shared logging, directory, hashing, and safe copy helpers
- `scripts/common-prereq-check.sh` - reusable prerequisite runner for package-local wrappers
- `scripts/common-export-helper.sh` - reusable export helpers and bundle note helpers
- `docs/git-repo-setup.md` - guide for making each package co-dev clone friendly
- `templates/package.gitignore` - starter `.gitignore` for package repos
- `examples/new-package-template/` - example package skeleton that consumes `_common`

## How package-specific reusables should consume it

From a package-local script, resolve both the package root and the shared `_common` path first:

```bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../_common" && pwd)"

# shellcheck source=/dev/null
source "$COMMON_DIR/scripts/common-lib.sh"
```

### Reusable prerequisite wrapper

Package-local `scripts/00-prereq-check.sh` should stay tiny and call the shared helper:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../_common" && pwd)"
# shellcheck source=/dev/null
source "$COMMON_DIR/scripts/common-prereq-check.sh"

PACKAGE_OPTIONAL_TOOLS=(ss ip systemctl nmap)
COMMON_OPTIONAL_TOOLS+=("${PACKAGE_OPTIONAL_TOOLS[@]}")
common_run_prereq_check "$ROOT_DIR" "my-package" sha256sum
```
```

### Reusable export wrapper

Package-local export scripts can source `common-export-helper.sh`, stamp package deliverables, then run package-specific export steps.

## Extension guidance

Use `_common` for:
- base shell behavior
- repeatable report/export workflow pieces
- docs shared across many packages

Keep package-local scripts for:
- target-specific filenames
- assessment-specific tooling
- report naming conventions
- custom evidence collection logic

## Git-repo-per-package workflow

Each package can be promoted into its own repository for collaboration.

Recommended approach:
1. copy or move the package folder into its own repo root
2. choose how `_common` is consumed, either vendored copy, git subtree, or git submodule
3. include the starter `.gitignore` from `templates/package.gitignore`
4. keep package-local wrappers thin so syncing common logic stays easy

See `docs/git-repo-setup.md` for the full workflow.
