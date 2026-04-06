# Reusable Utilities

This directory contains stable, reusable utilities for use across the workspace.

## CVE Lookup

**File:** `cve_lookup.py`

A stable wrapper entrypoint for CVE lookups that delegates to the existing implementation in `vuln/scripts/cve_lookup.py`.

### Usage

```bash
# Single service lookup
python3 scripts/opencode/reusable/cve_lookup.py --service openssh --version "8.2p1"

# Batch analyze enum JSON
python3 scripts/opencode/reusable/cve_lookup.py --file engagements/<target>/enum/parsed/nmap-service-*.json

# Specific CVE lookup
python3 scripts/opencode/reusable/cve_lookup.py --cve CVE-2024-6387

# Local exploit database only
python3 scripts/opencode/reusable/cve_lookup.py --service apache --version "2.4.49" --searchsploit-only

# Show wrapper info
python3 scripts/opencode/reusable/cve_lookup.py --wrapper-info
```

### Purpose

This wrapper provides:
- A stable, discoverable entrypoint under `scripts/opencode/reusable/`
- Delegation to the existing `vuln/scripts/cve_lookup.py` implementation
- Additional `--wrapper-info` flag for debugging

## Adding New Utilities

When adding new reusable utilities:
1. Place them in this directory
2. Add usage documentation to this README
3. Ensure they have proper `--help` output
4. Test with safe, non-destructive validation
