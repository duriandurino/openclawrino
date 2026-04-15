# New Reusable Package Template

This is a starter package showing how to consume `reusable_package/_common` from a package-local wrapper.

## Expected layout

This example assumes it sits at:

- `reusable_package/_common/`
- `reusable_package/<your-package>/`

If you promote the package into its own repo, either vendor `_common`, make it a subtree, or make it a submodule.

## Quick start

```bash
bash scripts/00-prereq-check.sh
bash scripts/95-export-bundle.sh
```

## What this demonstrates

- thin package-local wrappers
- package-specific optional tools layered on top of `_common`
- stamped report exports
- git-friendly structure for later repo extraction
