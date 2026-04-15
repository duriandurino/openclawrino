# Common Layer Integration Notes

This package now demonstrates how a reusable package can consume the shared layer at `reusable_package/_common/`.

## What changed

- `scripts/00-prereq-check.sh` now sources `_common/scripts/common-prereq-check.sh`
- `scripts/95-export-bundle.sh` now sources `_common/scripts/common-export-helper.sh`
- package-specific behavior still stays local, while shared logic moved into `_common`

## Why this matters

This keeps package wrappers thin and makes future reusable packages easier to build consistently.

The shared layer now handles:
- base logging and utility helpers
- base prerequisite checking behavior
- shared bundle-note generation
- reusable stamped export helpers

The Player V2 package still owns:
- package-specific optional tool expectations
- Player V2 naming conventions
- slide outline generation
- target-specific report files

## Suggested migration pattern for future packages

1. keep target-specific logic in `scripts/`
2. move generic shell helpers into `_common/scripts/`
3. document package assumptions in the package README
4. keep relative path resolution only, so the package can later become its own repo

## If this package becomes its own repository

Choose one of these:
- vendor `_common` into the repo
- include `_common` as a subtree
- include `_common` as a submodule

See `../../_common/docs/git-repo-setup.md` for the collaboration tradeoffs.
