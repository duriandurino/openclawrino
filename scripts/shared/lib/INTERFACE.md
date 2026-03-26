# Script Interface Standard

Use this as the contract for new automation.

## Required behavior

1. Validate inputs early.
2. Fail clearly when dependencies are missing.
3. Write outputs into predictable engagement paths.
4. Emit human-readable status to stdout.
5. Save structured JSON whenever parsing is possible.
6. Never overstate findings; label candidates clearly.

## Recommended arguments

### Common target selectors
- `--target <host-or-url>`
- `--domain <fqdn>`
- `--cidr <network>`
- `--host <single-host>`

### Common control flags
- `--engagement <name>`
- `--output-dir <path>`
- `--timeout <seconds>`
- `--safe`
- `--input <path>`
- `--profile <name>`
- `--format <json|markdown|text>`

## Output contract

Recommended paths:

```text
engagements/<engagement>/<phase>/
├── raw/
├── parsed/
└── summaries/
```

Example filenames:

- `raw/nmap-quick-<target>-<timestamp>.txt`
- `parsed/services-<target>-<timestamp>.json`
- `summaries/enum-quick-<target>-<timestamp>.md`

## JSON minimum fields

```json
{
  "target": "192.168.0.227",
  "phase": "enum",
  "script": "enum/ports/scan_ports_fast.sh",
  "timestamp": "2026-03-26T09:00:00+08:00",
  "status": "success",
  "findings": [],
  "artifacts": {
    "raw": "...",
    "parsed": "...",
    "summary": "..."
  }
}
```

## Exit codes

- `0` success
- `1` runtime failure
- `2` bad input
- `3` missing dependency
- `4` no useful result / target unavailable

## Safety labels

Scripts should state one of:

- `safe` - low-impact / passive or standard checks
- `moderate` - active probing with ordinary operational risk
- `high-risk` - potentially disruptive; ask before use
