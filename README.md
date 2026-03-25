# openclawrino

Workspace for **Hatless White / Specter** on OpenClaw.

This repository is the active pentest workspace: agent identities, custom skills, engagement artifacts, reporting pipeline, and operational notes all live here.

## What this repo is for

This workspace is used to:
- run structured penetration testing engagements
- orchestrate phase-based pentest sub-agents
- store engagement outputs under `engagements/`
- maintain custom OpenClaw skills for pentest methodology and reporting
- generate branded pentest deliverables (Doc, PDF, Slides)

## Core workspace files

- `AGENTS.md` — workspace operating rules and continuity guidance
- `SOUL.md` — persona / working style for Hatless White
- `USER.md` — operator context
- `TOOLS.md` — local environment notes
- `MEMORY.md` — curated long-term memory for the main session

## Main directories

### `agents/`
Identity and guardrail files for Specter sub-agents:
- `specter-recon.md`
- `specter-enum.md`
- `specter-vuln.md`
- `specter-exploit.md`
- `specter-post.md`
- `specter-report.md`

These files define each agent’s role and now also point to methodology skills when stronger phase discipline is needed.

### `skills/`
Custom OpenClaw skills used by the main session and sub-agents.

#### General / orchestration
- `cipher/` — general-purpose non-pentest technical assistant
- `pentest-orchestrator/` — multi-phase pentest orchestration
- `pentest-essentials/` — broad pentest methodology and fundamentals
- `preengagement-essentials/` — authorization, scope, and ROE discipline

#### Phase-specific methodology skills
- `enum-phase-essentials/`
- `vuln-phase-essentials/`
- `exploit-phase-essentials/`
- `post-phase-essentials/`
- `report-phase-essentials/`

These are **real implementation**, not memory-only notes:
- each exists as a workspace skill directory
- each has references/examples
- each has been validated and packaged into a `.skill` artifact
- each is integrated into relevant Specter agent files and/or the orchestrator

#### Reporting / presentation
- `presentation/`
- `pentest-slides/`
- `slides-cog/`
- `calendar-log/`
- `gworkspace/`

### `engagements/`
Stores engagement artifacts by target.

Expected structure:

```text
engagements/<target-name>/
├── SCOPE_<target>_<YYYY-MM-DD>.md
├── recon/
├── enum/
├── vuln/
├── exploit/
├── post-exploit/
└── reporting/
```

Phase handoff files follow the required naming convention:
- `RECON_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `ENUM_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `VULN_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `EXPLOIT_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `POST_EXPLOIT_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `REPORT_FINAL_<YYYY-MM-DD_HHMM>.md`

### `reporting/`
Reporting pipeline and branded publishing logic.

Primary production path:
- `reporting/scripts/generate_report.py`

Supporting implementation:
- `scripts/pentest_pptx_generator.py`
- `scripts/upload_pptx_to_drive.py`
- branding assets under `assets/`

## Reporting pipeline

For real finalized engagements, reporting is expected to produce:
- local markdown report
- published Google Doc
- PDF link
- Google Slides deck

The branded production path is:
- `reporting/scripts/generate_report.py`

Fallback-only path:
- raw `gog docs/slides` from markdown

## Current methodology stack

The workspace now includes phase-oriented methodology skills for:
- pre-engagement / ROE
- pentest fundamentals
- enumeration
- vulnerability analysis
- exploitation
- post-exploitation
- reporting

These are wired into the relevant Specter agents and `pentest-orchestrator` so the agentic environment can apply them during real engagements.

## Git / repo behavior

This repository is actively updated by the OpenClaw assistant during real work.
Commits are intended to persist actual implementation changes in the workspace, not just chat-memory decisions.

## Notes

- `memory/` is for local continuity and may not be fully tracked in git
- reports and evidence may contain sensitive material; handle with care
- real testing must pass authorization / scope / ROE checks before intrusive actions begin
