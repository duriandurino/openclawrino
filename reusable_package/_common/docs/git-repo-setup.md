# Git Repo Setup for Reusable Packages

This guide makes each reusable package easy to split into its own repository for co-development, review, and cloning.

## Goal

A package under `reusable_package/<package-name>/` should be able to become:
- its own standalone git repository
- a repo that still reuses `_common`
- something a collaborator can clone without extra tribal knowledge

## Recommended package shape

A package repo should keep:
- `README.md`
- `docs/`
- `scripts/`
- `reports/`
- `results/`
- `logs/`
- `templates/`
- `slides/` when presentations matter

If the package stays inside this workspace, `_common/` can live beside it.
If the package becomes its own repo, choose one of the sync patterns below.

## Options for consuming `_common`

### Option 1: Vendor `_common` into the package repo

Best when:
- you want the easiest clone experience
- the package is shared with less technical collaborators
- you accept manual syncing from upstream `_common`

Approach:
1. copy `_common/` into the repo
2. keep wrappers pointing at `./_common`
3. periodically sync common changes manually

### Option 2: Use git subtree

Best when:
- you want a single clone with no extra submodule steps
- you want traceable sync points from a shared common repo

Benefits:
- collaborators clone once and everything is present
- updates from common can be pulled in cleanly

Tradeoff:
- subtree workflow is a little more advanced than vendoring

### Option 3: Use git submodule

Best when:
- your team is comfortable with submodules
- you want `_common` versioned independently

Benefits:
- clean separation of package content and shared logic
- easy to pin common layer versions

Tradeoff:
- collaborators must remember `git clone --recurse-submodules` or run `git submodule update --init --recursive`

## Suggested repo bootstrap

Inside a package root after splitting it out:

```bash
git init
cp ../_common/templates/package.gitignore .gitignore
git add .
git commit -m "Initial reusable package import"
```

If `_common` is being vendored, copy it before the first commit.
If `_common` is a submodule, add it before or right after the first commit.

## Wrapper script rule

Keep package scripts as wrappers around shared helpers where possible.
That way, when a collaborator clones only the package repo, the integration points are obvious and thin.

## Collaboration notes

- document the expected `_common` location in `README.md`
- prefer relative path resolution in scripts
- avoid hard-coded absolute workspace paths
- keep package naming and stamped outputs deterministic
- commit templates and docs, not bulky generated artifacts unless the workflow truly needs them

## Co-dev clone checklist

A collaborator should be able to:
1. clone the package repo
2. read one README
3. run the prerequisite check
4. understand how `_common` is supplied
5. generate the report bundle without asking for hidden setup knowledge
