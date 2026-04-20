# reusable_package Repository Setup

This file explains how to make `reusable_package/` itself a standalone repository for co-dev collaboration.

## Recommended approach

From the workspace root:

```bash
cd reusable_package
git init
git add .
git commit -m "Initial reusable package repository"
```

If you want to publish it to GitHub or another forge:

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## What belongs in this repo
- `_common/`
- reusable package folders like `player-v2-direct-2026-04-15_1205/`
- shared docs, templates, and examples

## What generally should not be committed
- transient logs
- temporary run folders
- bulky generated export files unless intentionally curated
- local-only evidence copies unless the team explicitly wants them versioned

The included root `.gitignore` already covers the common generated paths.

## Parent workspace relationship
You asked specifically for `reusable_package/` to be the repo root itself.
That means this directory can stand alone without forcing each package into a separate repository first.

Later, if you want tighter separation, individual packages can still be split out into their own repos.

## Optional next step
If you want the parent workspace to reference this new repo cleanly, the clean follow-up is:
- remove `reusable_package/` from the parent repo tracking model
- add it back as a git submodule or subtree

I did not do that automatically here, because it changes the parent repo relationship and is worth doing deliberately.
