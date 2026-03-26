# quick-scan/

Fast security triage profiles that reuse recon/enum/vuln wrappers and generate a compact report.

## Profiles
- `webapp` - HTTP/web-focused quick check
- `api` - safe API-focused quick check
- `host` - generic host/service quick check
- `pc` - workstation/Windows-oriented quick check
- `player` - IoT / player quick check

## Main entry point

```bash
python3 scripts/quick-scan/run_quick_scan.py --profile webapp --target https://example.com
```

## Outputs

```text
engagements/<engagement>/
├── recon/
├── enum/
├── vuln/
└── quick-scan/
    └── reporting/
```

## Deliverables
- `QUICK_SCAN_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `QUICK_SCAN_REPORT_<YYYY-MM-DD_HHMM>.md`

## Notes
- This is rapid triage, not a full pentest.
- Findings are candidate-oriented unless explicitly verified.
