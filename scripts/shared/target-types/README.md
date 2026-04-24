# full-pentest target families

This directory holds reusable target-family composition data for **full pentest workflows**.

It is intentionally separate from `scripts/quick-scan/profiles/`.

## Why this exists

Quick scans answer, "what is the fastest safe triage path?"

Full pentests answer, "what families of attack surface are likely present, and which reusable manifests should anchor each phase?"

That means full-pentest target families should:
- compose multiple sub-families when the target is hybrid
- recommend phase entrypoints, not just a single fast profile
- preserve analyst judgment and manual branching
- stay evidence-first and authorization-aware

## Current families

- `linux-host`
- `raspi`
- `electron-app`
- `python-app`
- `player`
- `player-pulselink`

## Data model

`families.yaml` defines:
- family descriptions
- inheritance via `extends`
- tags and target kinds
- default phase entrypoints
- recommended manifests per phase
- analyst notes and capability hints
- named manifest sets for orchestration helpers

## Usage pattern

1. Recommend a family from target hints.
2. Review the composed phase plan.
3. Run the recommended manifest(s) as the reusable baseline.
4. Add manual/ad hoc phase work based on live evidence.

Example:

```bash
python3 scripts/orchestration/recommend_target_family.py --hint "Raspberry Pi player kiosk with Electron UI, Python service, MQTT, PulseLink"
python3 scripts/orchestration/describe_target_family.py --family player-pulselink
```

## Design rules

- Do not overwrite the analyst's plan.
- Do not pretend every phase has complete automation.
- Prefer small manifest bundles over giant frameworks.
- Keep existing phase scripts/manifests intact, then compose them here.
- Add new manifests only when they clearly improve a reusable phase baseline.
