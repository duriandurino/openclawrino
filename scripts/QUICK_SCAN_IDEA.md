# Quick Scan Idea — Reusable Security Check + Report

This is the follow-on concept after phase summary automation.

## Goal

Create a fast, low-friction security check mode that can assess:
- web applications
- PCs / workstations
- Players / IoT devices
- APIs
- generic hosts or services

And then automatically produce:
- raw artifacts
- parsed findings
- a quick assessment report

## Design direction

Use the same architecture already built:
- wrappers do the repeatable checks
- profile runners choose the right flow
- summary/report generators turn artifacts into deliverables

## Likely structure

```text
scripts/quick-scan/
├── profiles/
│   ├── webapp.yaml
│   ├── pc.yaml
│   ├── api.yaml
│   ├── player.yaml
│   └── host.yaml
├── run_quick_scan.py
└── generate_quick_report.py
```

## Candidate quick scan profiles

### webapp
- HTTP fingerprint
- header review
- robots.txt
- path discovery (safe)
- basic vuln web baseline

### pc / host
- fast port scan
- service scan
- SMB/RDP/WinRM checks when relevant
- version-to-CVE candidate mapping

### api
- headers
- methods/options
- auth-related response behavior
- common docs endpoint discovery (`/swagger`, `/openapi.json`, `/docs`)

### player / IoT
- fast scan
- web baseline if web UI exists
- service probes (MQTT, SSH, HTTP, SMB if exposed)
- version exposure and default-surface checks

## Outputs

```text
engagements/<target>/quick-scan/
├── raw/
├── parsed/
├── summaries/
└── reporting/
```

## Deliverables

- `QUICK_SCAN_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `QUICK_SCAN_REPORT_<YYYY-MM-DD_HHMM>.md`

## Reuse plan

The quick scan feature should reuse:
- `scripts/orchestration/run_*_profile.py`
- phase wrappers under `scripts/recon/`, `scripts/enum/`, `scripts/vuln/`
- `scripts/orchestration/generate_phase_summary.py`

## Principle

This is not a full pentest. It is a rapid triage / hygiene / exposure assessment mode with report output.
