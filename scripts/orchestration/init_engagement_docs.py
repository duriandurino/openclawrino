#!/usr/bin/env python3
"""Initialize a documentation-first pentest engagement structure."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGAGEMENTS = ROOT / "engagements"

PHASE_DIRS = [
    "pre-engagement",
    "recon",
    "enum",
    "vuln",
    "exploit",
    "post-exploit",
    "reporting",
    "evidence/screenshots",
    "evidence/pcaps",
    "evidence/transcripts",
    "evidence/payloads",
    "evidence/notes",
    "registers",
    "reports",
]

PHASE_FILES = {
    "recon": [
        "recon-summary.md",
        "recon-activity-log.md",
        "recon-evidence-index.md",
        "recon-findings-delta.md",
        "recon-next-actions.md",
    ],
    "enum": [
        "enum-summary.md",
        "enum-activity-log.md",
        "enum-evidence-index.md",
        "enum-findings-delta.md",
        "enum-next-actions.md",
    ],
    "vuln": [
        "vuln-summary.md",
        "vuln-validation-log.md",
        "vuln-evidence-index.md",
        "vuln-findings-delta.md",
        "vuln-next-actions.md",
    ],
    "exploit": [
        "exploit-summary.md",
        "exploit-activity-log.md",
        "exploit-evidence-index.md",
        "exploit-findings-delta.md",
        "exploit-next-actions.md",
        "attack-paths.md",
    ],
    "post-exploit": [
        "post-exploit-summary.md",
        "loot-and-impact-log.md",
        "post-exploit-evidence-index.md",
        "post-exploit-findings-delta.md",
        "post-exploit-next-actions.md",
        "cleanup-notes.md",
    ],
    "reporting": [
        "executive-report.md",
        "technical-report.md",
        "appendix.md",
        "presentation-outline.md",
        "process-overview.md",
    ],
}


def ensure_text(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def build_charter(args: argparse.Namespace) -> str:
    return f"""# Engagement Charter

- **Engagement title:** {args.title}
- **Target:** {args.target}
- **Test type:** {args.test_type}
- **Start date:** {args.start_date}
- **End date:** {args.end_date}
- **Status:** {args.status}
- **Approval / authorization reference:** {args.approval}
- **Success criteria:** {args.success_criteria}
- **Primary analyst:** Hatless White
- **Supporting agents:** specter-recon, specter-enum, specter-vuln, specter-exploit, specter-post, specter-report

## Objectives

- TBD

## Constraints

- {args.constraints}

## Credentials Provided

- {args.credentials}

## Communications

- **Primary contact:** TBD
- **Escalation contact:** TBD
- **Stop condition contact:** TBD

## Notes

- Initialized by `scripts/orchestration/init_engagement_docs.py`
"""


def build_scope(args: argparse.Namespace) -> str:
    return f"""# Scope and Rules of Engagement

## Scope In

- {args.scope_in}

## Scope Out

- {args.scope_out}

## Rules of Engagement

- **Testing window:** {args.testing_window}
- **Allowed techniques:** TBD
- **Prohibited techniques:** TBD
- **DoS allowed?:** no
- **Persistence allowed?:** TBD
- **Social engineering allowed?:** TBD
- **Third-party / cloud approvals:** TBD

## Safety Controls

- **Blackout periods:** TBD
- **Fragile systems / constraints:** {args.constraints}
- **Emergency stop conditions:** TBD
- **Resume authority:** TBD

## Data Handling

- **Collection limits:** TBD
- **Storage expectations:** workspace engagement folders only
- **Retention / destruction:** TBD
- **Sensitive data handling:** redact secrets from shared reporting

## Approval Status

- **Authorization confirmed?:** {args.authorization_confirmed}
- **Provider approvals confirmed?:** TBD
- **Cleared for active testing?:** {args.cleared_for_testing}

## Notes

- Initialized by `scripts/orchestration/init_engagement_docs.py`
"""


def placeholder(title: str, body: str) -> str:
    return f"# {title}\n\n{body}\n"


def slugify_title(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return cleaned or "engagement"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize engagement docs structure")
    parser.add_argument("engagement", nargs="?", default="")
    parser.add_argument("--title", default="TBD")
    parser.add_argument("--target", default="TBD")
    parser.add_argument("--test-type", default="TBD")
    parser.add_argument("--start-date", default="TBD")
    parser.add_argument("--end-date", default="TBD")
    parser.add_argument("--status", default="intake")
    parser.add_argument("--approval", default="TBD")
    parser.add_argument("--success-criteria", default="TBD")
    parser.add_argument("--constraints", default="TBD")
    parser.add_argument("--credentials", default="TBD")
    parser.add_argument("--scope-in", default="TBD")
    parser.add_argument("--scope-out", default="TBD")
    parser.add_argument("--testing-window", default="TBD")
    parser.add_argument("--authorization-confirmed", default="TBD")
    parser.add_argument("--cleared-for-testing", default="no")
    args = parser.parse_args()

    engagement_name = (args.engagement or "").strip()
    title = (args.title or "").strip()
    if not engagement_name:
        engagement_name = slugify_title(title)
    args.engagement = engagement_name

    base = ENGAGEMENTS / args.engagement
    for rel in PHASE_DIRS:
        (base / rel).mkdir(parents=True, exist_ok=True)

    ensure_text(base / "pre-engagement" / "engagement-charter.md", build_charter(args))
    ensure_text(base / "pre-engagement" / "scope-and-roe.md", build_scope(args))

    for folder, files in PHASE_FILES.items():
        for name in files:
            path = base / folder / name
            ensure_text(path, placeholder(name.replace("-", " ").replace(".md", "").title(), "- TBD"))

    ensure_text(base / "registers" / "master-activity-log.md", placeholder("Master Activity Log", "- Initialize entries here as work begins"))
    ensure_text(base / "registers" / "findings-register.md", "# Findings Register\n\n| Finding ID | Status | Title | Affected asset | Evidence | Impact | Likelihood | Risk | CVSS | Remediation |\n|---|---|---|---|---|---|---|---|---|---|\n")
    ensure_text(base / "registers" / "evidence-register.md", "# Evidence Register\n\n| Evidence ID | Phase | Type | Source | Timestamp | Related finding | Sensitivity | Storage path | Sanitized? |\n|---|---|---|---|---|---|---|---|---|\n")
    ensure_text(base / "registers" / "attack-path-register.md", placeholder("Attack Path Register", "- Add attack paths here when findings chain together"))
    ensure_text(base / "registers" / "asset-register.md", "# Asset Register\n\n| Asset ID | Asset | Type | Scope status | Notes |\n|---|---|---|---|---|\n")
    ensure_text(
        base / "reports" / "README.md",
        "# Engagement User Input Reports\n\n"
        "Store filled user engagement input templates here.\n\n"
        "## Naming\n\n"
        "- `<engagement-name>-user-input-YYYY-MM-DD-HHMM.md`\n"
        "- `user-input-YYYY-MM-DD-HHMM.md` when engagement context is not settled yet\n\n"
        "## Handling Rules\n\n"
        "- Do not overwrite prior user submissions unless explicitly instructed.\n"
        "- Treat each submission as source context material for the engagement trail.\n"
        "- Parse and map actions, findings, evidence, failed attempts, pivots, and unclassified notes into the relevant phase docs and shared registers.\n"
        "- Preserve low-confidence or unclassified entries in a traceable form until classification is clearer.\n",
    )

    print(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
