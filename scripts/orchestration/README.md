# orchestration/

Profile and manifest-driven runners live here.

## Purpose

Let agents choose a workflow profile instead of planning every command from scratch.

Before manual phase planning for a full pentest, prefer the reusable target-family layer:

- `recommend_target_family.py` suggests a full-pentest target family from free-text hints
- `describe_target_family.py` expands the family into composed phase guidance and baseline manifests
- `plan_target_family.py` turns a chosen family into a concrete per-phase execution plan with resolved manifests and step-level script calls
- family data lives under `scripts/shared/target-types/`

Examples:

- `run_recon_profile.py --profile external-web --target example.com`
- `run_enum_profile.py --profile windows-host --target 192.168.0.227`
- `run_vuln_profile.py --profile web-service --target 192.168.0.227 --input engagements/.../enum/parsed/services.json`
- `recommend_target_family.py --hint "Raspberry Pi player kiosk with Electron UI and MQTT"`
- `describe_target_family.py --family player-pulselink`
- `plan_target_family.py --family player-pulselink --target 192.168.0.50 --engagement engagements/player-v2`
- `plan_target_family.py --hint "Raspberry Pi player kiosk with Electron UI, Python service, MQTT" --target 192.168.0.50 --engagement engagements/player-v2`
- `init_engagement_docs.py player-v2 --title "Player V2 Assessment" --target "player-v2"`
- `init_engagement_docs.py --title "Player V2 Assessment" --target "player-v2"`  # engagement slug derived from title

## Documentation-first helpers

- `init_engagement_docs.py` creates the standardized engagement folder layout, charter, ROE file, phase deliverables, evidence folders, central registers, and a per-engagement `reports/` folder for user-filled input submissions.
- `generate_phase_summary.py` drafts standardized phase handoffs from parsed artifacts, but the handoff still needs analyst review and the phase activity log / evidence / findings docs kept current.
- `templates/user-engagement-input-template.md` is the reusable manual-input boilerplate for user-controlled pentest activity capture.
- Filled user templates should be saved under `engagements/<target-name>/reports/` when engagement context is known, or `reports/` as a shared intake location when it is not.

## Design

- for full pentests, choose a target family first when the target type is known or inferable
- expand that family into phase entrypoints and recommended baseline manifests
- use `plan_target_family.py` as the dispatcher/helper that resolves the family into an actionable per-phase baseline
- read manifests from `scripts/shared/manifests/`
- validate target and dependencies
- execute steps in order
- store artifacts under engagement phase directories
- emit one execution summary at the end
- keep documentation artifacts current alongside execution artifacts
- absorb user-submitted markdown activity into the same engagement trail, including tentative or unclassified notes
