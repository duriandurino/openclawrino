# Task Tracker — Engagement Cleanup Naming and Pre-Engagement

**Created:** 2026-04-17 15:19 Asia/Manila
**Status:** implementation in progress
**Owner:** Hatless White

## Objective

Normalize engagement folder and file naming across the current workspace implementation, replace `00-charter/` with `pre-engagement/`, and prepare for a title-derived engagement directory naming model so repeated work stays inside one engagement directory with timestamped artifacts.

## Scope Currently Included

- Map current implementation naming conventions
- Define cleanup and migration targets
- Replace `00-charter/` with `pre-engagement/`
- Normalize phase folder names to flat canonical names
- Prevent future round-based engagement directory sprawl
- Introduce engagement-title-derived directory naming
- Add easy-to-call aliases for pentest phase agents
- Track implementation tasks and progress in this note

## Decisions Captured So Far

- Canonical pre-engagement folder should be `pre-engagement/`
- Canonical phase folders should be:
  - `recon/`
  - `enum/`
  - `vuln/`
  - `exploit/`
  - `post-exploit/`
  - `reporting/`
- Numbered folder names like `01-recon/` and `06-report/` should be retired from active generation
- Engagement directory name should be derived from the pre-engagement title using a filesystem-safe slug
- Repeated work on the same engagement should create new timestamped files, not new sibling directories like `*-round2`
- Pentest phase agents should support easy-to-call names:
  - `Rico` -> reconnaissance
  - `Ena` -> enumeration
  - `Viol` -> vulnerability check
  - `Loid` -> exploitation
  - `Post` -> post exploitation
  - `Raph` -> reporting
- Confirmed alias policy for current implementation:
  - keep current `specter-*` agent IDs as the execution/runtime identities
  - use the easy-to-call names as user-facing shorthand for phases or sub-agents in chat and task descriptions
  - aliases are primarily for easier human reference, for example `inspect Raph output` instead of only saying `inspect report output`
  - map aliases as follows:
    - `Rico` -> `specter-recon`
    - `Ena` -> `specter-enum`
    - `Viol` -> `specter-vuln`
    - `Loid` -> `specter-exploit`
    - `Post` -> `specter-post`
    - `Raph` -> `specter-report`
  - do not rename runtime agent IDs

## Checklist

- [x] Inspect current workspace naming conventions from live implementation
- [x] Identify mixed legacy vs docs-first engagement layouts
- [x] Identify current hardcoded `00-charter` references
- [x] Draft cleanup map for target naming model
- [x] Write final implementation spec for naming rules, compatibility rules, and migration rules
- [x] Update `scripts/orchestration/init_engagement_docs.py` to generate canonical folder names
- [x] Update `reporting/scripts/generate_report.py` to read `pre-engagement/` first
- [x] Add compatibility fallback in report loading for legacy `00-charter/`
- [x] Update `skills/pentest-orchestrator/SKILL.md` path references
- [x] Update `skills/pentest-orchestrator/references/engagement-doc-templates.md`
- [x] Update `skills/pentest-orchestrator/references/engagement-documentation-protocol.md`
- [x] Define slug generation rule from engagement title
- [x] Define how easy-to-call phase-agent aliases map to current specter agents and prompts
- [x] Decide whether `SCOPE_<engagement>_<YYYY-MM-DD>.md` remains primary, compatibility-only, or retired
- [x] Define migration plan for existing engagements
- [x] Identify and merge fragmented engagements like PlayerV2 rounds if explicitly requested
- [x] Verify no active workflow still depends on numbered phase directories only
- [ ] Commit changes in workspace
- [ ] Push changes to repo

## Proposed Implementation Spec

### Canonical engagement structure

Use one canonical full-engagement structure:

- `engagements/<engagement-slug>/pre-engagement/`
- `engagements/<engagement-slug>/recon/`
- `engagements/<engagement-slug>/enum/`
- `engagements/<engagement-slug>/vuln/`
- `engagements/<engagement-slug>/exploit/`
- `engagements/<engagement-slug>/post-exploit/`
- `engagements/<engagement-slug>/reporting/`
- `engagements/<engagement-slug>/evidence/`
- `engagements/<engagement-slug>/registers/`
- `engagements/<engagement-slug>/reports/`

### Folder rename targets

- `00-charter/` -> `pre-engagement/`
- `01-recon/` -> `recon/`
- `02-enum/` -> `enum/`
- `03-vuln/` -> `vuln/`
- `04-exploit/` -> `exploit/`
- `05-post-exploit/` -> `post-exploit/`
- `06-report/` -> `reporting/`
- `report/` -> `reporting/`
- `post/` -> `post-exploit/`

### Pre-engagement source of truth

Primary files:
- `pre-engagement/engagement-charter.md`
- `pre-engagement/scope-and-roe.md`

Compatibility file:
- `SCOPE_<engagement-slug>_<YYYY-MM-DD>.md` is compatibility-only for older workflows

### Engagement naming rule

- derive the engagement directory name from the pre-engagement title
- convert the title to a filesystem-safe slug
- slug rule:
  - normalize unicode to ASCII where possible
  - lowercase the result
  - replace any run of non-alphanumeric characters with a single `-`
  - trim leading and trailing `-`
  - fallback to `engagement` if the result becomes empty
- keep the target as a separate field from the directory name
- `init_engagement_docs.py` should accept either an explicit engagement name or derive it from `--title`
- repeated work for the same engagement should add new timestamped files inside the same engagement directory, not create sibling `*-roundN` directories

### Versioned artifact rule

Keep timestamped filenames for generated handoff and deliverable artifacts:
- `RECON_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `ENUM_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `VULN_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `EXPLOIT_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `POST_EXPLOIT_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `REPORT_FINAL_<YYYY-MM-DD_HHMM>.md`
- `EXECUTIVE_SUMMARY_<YYYY-MM-DD_HHMM>.md`
- `REMEDIATION_GUIDE_<YYYY-MM-DD_HHMM>.md`

### Working-doc rule

Keep lower-case living working docs inside each phase directory, for example:
- `recon-summary.md`
- `enum-summary.md`
- `vuln-summary.md`
- `exploit-summary.md`
- `post-exploit-summary.md`
- `technical-report.md`
- `executive-report.md`

### Compatibility rule

During migration, readers should support both old and new locations where practical:
- prefer `pre-engagement/`
- fall back to `00-charter/`
- prefer flat canonical phase names
- tolerate numbered phase directories during transition

### Agent alias rule

Confirmed current policy:
- keep runtime IDs unchanged:
  - `specter-recon`
  - `specter-enum`
  - `specter-vuln`
  - `specter-exploit`
  - `specter-post`
  - `specter-report`
- support user-facing aliases for easier reference in chat, planning, and review:
  - `Rico` -> `specter-recon`
  - `Ena` -> `specter-enum`
  - `Viol` -> `specter-vuln`
  - `Loid` -> `specter-exploit`
  - `Post` -> `specter-post`
  - `Raph` -> `specter-report`
- aliases are shorthand only, not runtime renames

## Current Findings

### Current layout reality

There are two active styles in the workspace:

1. Legacy/simple layout
   - `recon/`, `enum/`, `vuln/`, `exploit/`, `post-exploit/`, `reporting/`
   - timestamped summary artifacts like `ENUM_SUMMARY_<YYYY-MM-DD_HHMM>.md`

2. Newer docs-first layout
   - `00-charter/`, `01-recon/`, `02-enum/`, `03-vuln/`, `04-exploit/`, `05-post-exploit/`, `06-report/`
   - lower-case working docs like `recon-summary.md`, `technical-report.md`

### Confirmed hardcoded / implementation references

- `scripts/orchestration/init_engagement_docs.py`
- `reporting/scripts/generate_report.py`
- `skills/pentest-orchestrator/SKILL.md`
- `skills/pentest-orchestrator/references/engagement-doc-templates.md`
- `skills/pentest-orchestrator/references/engagement-documentation-protocol.md`
- `scripts/orchestration/README.md`

### Observed fragmentation problem

Current workspace shows the repeated-engagement sprawl problem in PlayerV2-related directories, including:
- `engagements/playerv2-setup-enc`
- `engagements/playerv2-setup-enc-round2`
- `engagements/playerv2-setup-enc-round3`
- `engagements/playerv2-setup-enc-round4`
- and more

These should likely have been one engagement directory with multiple timestamped artifacts.

## Notes / Open Questions

- Need to define exact slugging behavior for engagement title to folder name
- Some engagement-specific helper scripts outside the primary implementation path may still contain old numbered folder references and should be handled selectively, not as part of mass migration
- Remaining old-path references found in `skills/presentation/SKILL.md` and an engagement-specific helper under `scripts/opencode/session/`; these are secondary follow-up items, not blockers for the current core cleanup
- `SCOPE_*.md` is confirmed as compatibility-only
- Easy-to-call names are confirmed as user-facing aliases only, not runtime renames
- Existing old directories should not be mass-migrated for now; use fallback/compatibility first
- Fragmented engagements like PlayerV2 rounds are deferred to a separate migration task
- Need explicit instruction before mass-renaming existing engagement folders

## Review Gate

### Ready for approval

This tracker is now ready for user review before implementation begins.

### Items that still need user confirmation

- none at the moment

## Change Log

- 2026-04-17 15:19 PST — Created tracker for engagement cleanup naming and pre-engagement refactor
- 2026-04-17 15:29 PST — Added easy-to-call phase-agent aliases: Rico, Ena, Viol, Loid, Post, Raph
- 2026-04-17 15:48 PST — Added alias mapping policy, implementation spec, and review gate
- 2026-04-17 15:58 PST — Confirmed aliases remain user-facing shorthand only; runtime agent IDs stay `specter-*`
- 2026-04-17 16:19 PST — Confirmed `SCOPE_*.md` is compatibility-only, old engagements are fallback-first with no mass migration now, and PlayerV2 round merging is a separate future migration task
- 2026-04-17 16:26 PST — Started implementation pass for canonical pre-engagement and phase naming updates
- 2026-04-17 16:27 PST — Updated initializer, reporting pre-engagement lookup, and pentest orchestrator docs to prefer canonical `pre-engagement/`, `recon/`, `enum/`, `vuln/`, `exploit/`, `post-exploit/`, and `reporting/` paths while preserving `00-charter/` fallback in report loading
- 2026-04-17 16:46 PST — Added title-to-slug behavior to `init_engagement_docs.py`, documented the slug rule, and completed a verification sweep that identified only secondary old-path references outside the primary cleanup path
