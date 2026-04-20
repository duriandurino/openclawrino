# Reusable Pentest Packages

This directory is now intended to be its own standalone git repository root for reusable pentest packages and shared package infrastructure.

## Purpose
This repo holds:
- reusable pentest package folders
- the shared `_common/` layer used by those packages
- package templates and collaboration guidance

Current contents include:
- `_common/` shared scripts, docs, templates, and examples
- `player-v2-direct-2026-04-15_1205/` as the first concrete reusable package

## Repository model
Treat `reusable_package/` as a portable collaboration repo for you and your co-devs.

Recommended structure:
- one repo for `reusable_package/`
- many reusable package folders inside it
- one shared `_common/` layer for prerequisite checks, export helpers, and common package behavior

This is better than splitting every package immediately because:
- collaborators clone once and get all reusables plus `_common`
- shared logic can evolve in one place
- new packages can be bootstrapped from a consistent pattern

## Quick start
From this repo root:

```bash
cd reusable_package
```

Inspect the shared layer:
```bash
ls _common
```

Run the Player V2 package prerequisite check:
```bash
bash player-v2-direct-2026-04-15_1205/scripts/00-prereq-check.sh
```

Run the Player V2 export bundle flow:
```bash
bash player-v2-direct-2026-04-15_1205/scripts/95-export-bundle.sh
```

## Git setup
To turn this directory into its own git repository:

```bash
cd reusable_package
git init
cp _common/templates/package.gitignore .gitignore
git add .
git commit -m "Initial reusable package repository"
```

If you later want to publish it:

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## Collaboration guidance
- keep package-specific logic inside package folders
- keep shared prereq/export utilities inside `_common/`
- prefer thin package wrappers over duplicated helper logic
- avoid hard-coded absolute paths so co-dev clones work cleanly

## Repo evolution options
Later, you can choose one of these:
1. keep `reusable_package/` as a single shared repo
2. split individual packages into separate repos when they mature
3. keep `_common/` here, or eventually spin `_common/` into its own repo if needed

## Important note
Generated logs, results, and bulky outputs should generally be ignored at the repo root unless you explicitly want them versioned.
Use the root `.gitignore` based on `_common/templates/package.gitignore` and extend it as needed.
