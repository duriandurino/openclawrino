# orchestration/

Profile and manifest-driven runners live here.

## Purpose

Let agents choose a workflow profile instead of planning every command from scratch.

Examples:

- `run_recon_profile.py --profile external-web --target example.com`
- `run_enum_profile.py --profile windows-host --target 192.168.0.227`
- `run_vuln_profile.py --profile web-service --target 192.168.0.227 --input engagements/.../enum/parsed/services.json`

## Design

- read manifest from `scripts/shared/manifests/`
- validate target and dependencies
- execute steps in order
- store artifacts under engagement phase directories
- emit one execution summary at the end
