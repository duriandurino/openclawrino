# quick-scan/

Fast security triage profiles that reuse recon/enum/vuln wrappers and generate a compact report.

## Profiles
- `webapp` - HTTP/web-focused quick check
- `webapp-deep` - deeper webapp triage with active path discovery
- `api` - safe API-focused quick check
- `api-auth` - API triage with docs/auth surface probing
- `graphql` - GraphQL endpoint and baseline security triage
- `nestjs-api` - NestJS/Swagger/OpenAPI-oriented API triage
- `webhook` - webhook/callback endpoint triage

Target-aware vuln baselines now exist for:
- GraphQL
- NestJS API
- Webhooks
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

Current export/publish behavior:
- always creates `.txt`
- always creates `.html`
- publishes through the main pentest report generator path when quick scan runs normally
- creates branded Google Doc / PDF preview / Slides via the production reporting flow when Google auth is available

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
- `EXECUTIVE_SUMMARY_QUICK_SCAN_<YYYY-MM-DD_HHMM>.md`
- `REPORT_QUICK_SCAN_<YYYY-MM-DD_HHMM>.md`
- `EXECUTIVE_SUMMARY_QUICK_SCAN_<YYYY-MM-DD_HHMM>.txt`
- `EXECUTIVE_SUMMARY_QUICK_SCAN_<YYYY-MM-DD_HHMM>.html`
- `REPORT_QUICK_SCAN_<YYYY-MM-DD_HHMM>.txt`
- `REPORT_QUICK_SCAN_<YYYY-MM-DD_HHMM>.html`
- `*.pdf` variants when converter support exists

## Notes
- This is rapid triage, not a full pentest.
- Findings are candidate-oriented unless explicitly verified.
- Use `--mode fast` to skip optional follow-up probes where supported.
- Prefer `webapp-deep`, `api-auth`, `player-pulselink`, or `iot-mqtt` when the target type is already known.
- See `scripts/quick-scan/DISPATCH.md` for the decision path between quick scan and full pentest workflows.
