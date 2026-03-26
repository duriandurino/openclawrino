# Pentest Automation Scripts

This directory holds reusable automation for engagement phases.

## Goals

- reduce repeated agent planning
- reduce token usage
- standardize outputs
- improve speed and consistency
- make phase handoffs easier

## Structure

```text
scripts/
├── shared/            # cross-phase helpers, parsers, templates, manifests
├── recon/             # passive / low-touch recon scripts
├── enum/              # active enumeration scripts
├── vuln/              # vulnerability analysis helpers
└── orchestration/     # profile runners and manifest dispatchers
```

## Script design rules

1. Small and composable beats giant monoliths.
2. Every script should have a single clear purpose.
3. Shared logic belongs under `shared/`.
4. Agents should select scripts or profiles, not rebuild workflows from scratch.
5. Output should be standardized so later phases can consume it.

## Standard interface

Every new script should support these conventions where practical:

- `--target <value>` or a clearly named equivalent (`--domain`, `--cidr`, `--host`)
- `--engagement <name>`
- `--phase <recon|enum|vuln>` when helpful
- `--output-dir <path>`
- `--format <json|markdown|text>` if multiple formats are supported
- `--timeout <seconds>` if the action can run long
- `--profile <name>` for orchestrators
- `--safe` for low-impact checks when relevant
- `--help`

## Standard outputs

Each script should aim to produce:

- raw artifact(s)
- parsed JSON
- short markdown summary

Recommended engagement layout:

```text
engagements/<target>/<phase>/
├── raw/
├── parsed/
└── summaries/
```

## Exit codes

- `0` success
- `1` runtime failure
- `2` invalid arguments or validation failure
- `3` dependency missing
- `4` target unreachable / no useful result

## Initial high-ROI roadmap

### Recon
- `recon/dns/recon_dns_baseline.py`
- `recon/whois/recon_whois_summary.sh`
- `recon/web/recon_http_fingerprint.sh`

### Enum
- `enum/ports/scan_ports_fast.sh`
- `enum/ports/scan_ports_service.sh`
- `enum/smb/enum_smb_basic.sh`
- `enum/web/enum_web_basic.sh`
- `enum/profiles/run_enum_profile.sh`

### Vuln
- `vuln/cve-mapping/map_versions_to_cves.py`
- `vuln/cve-mapping/searchsploit_auto.sh`
- `vuln/web/web_baseline.sh`
- `vuln/profiles/run_vuln_profile.sh`

## Existing phase scripts

Legacy phase-local scripts currently exist under:

- `recon/scripts/`
- `enum/scripts/`
- `vuln/scripts/`

Those can be migrated or wrapped gradually instead of rewritten all at once.
