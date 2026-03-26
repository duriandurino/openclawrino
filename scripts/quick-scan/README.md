# quick-scan/

Fast security triage profiles that reuse recon/enum/vuln wrappers and generate a compact report.

## Profiles
- `webapp` - HTTP/web-focused quick check
- `webapp-deep` - deeper webapp triage with active path discovery
- `api` - safe API-focused quick check
- `api-auth` - API triage with docs/auth surface probing
- `host` - generic host/service quick check
- `pc` - workstation/Windows-oriented quick check
- `player` - IoT / player quick check
- `player-pulselink` - PulseLink/player-oriented quick triage
- `iot-mqtt` - IoT/MQTT quick triage with broker exposure checks
- `windows-host` - Windows-focused quick host triage
- `linux-host` - Linux-focused quick host triage

## Main entry point

```bash
python3 scripts/quick-scan/run_quick_scan.py --profile webapp --target https://example.com
```

## Profile recommender

```bash
python3 scripts/quick-scan/recommend_profile.py --hint "windows workstation with smb and rdp"
python3 scripts/quick-scan/recommend_profile.py --hint "mqtt broker on an iot device" --json
```

## Report export

```bash
python3 scripts/quick-scan/export_quick_report.py --engagement <engagement>
```

Current export behavior:
- always creates `.txt`
- always creates `.html`
- creates `.pdf` when a supported converter is available

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
- `QUICK_SCAN_REPORT_<YYYY-MM-DD_HHMM>.txt`
- `QUICK_SCAN_REPORT_<YYYY-MM-DD_HHMM>.html`
- `QUICK_SCAN_REPORT_<YYYY-MM-DD_HHMM>.pdf` (optional when converter available)

## Notes
- This is rapid triage, not a full pentest.
- Findings are candidate-oriented unless explicitly verified.
- Use `--mode fast` to skip optional follow-up probes where supported.
- Prefer `webapp-deep`, `api-auth`, `player-pulselink`, or `iot-mqtt` when the target type is already known.
- See `scripts/quick-scan/DISPATCH.md` for the decision path between quick scan and full pentest workflows.
