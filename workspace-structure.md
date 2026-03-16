# Pentest Workspace Directory Structure

## Overview

This workspace is organized to support the full penetration testing lifecycle. Each engagement gets its own isolated folder, and shared resources live at the top level.

```
~/.openclaw/workspace/
├── 📂 engagements/              # Each pentest engagement lives here
│   └── raspi5-lab/              # Current target: Raspberry Pi 5
│       ├── recon/               # Phase 1: Passive recon, OSINT, DNS
│       │   └── README.md        # What to collect here
│       ├── enum/                # Phase 2: Active enumeration, port scans
│       │   └── README.md
│       ├── vuln/                # Phase 3: Vulnerability analysis
│       │   └── README.md
│       ├── exploit/             # Phase 4: Exploitation attempts & results
│       │   └── README.md
│       ├── post-exploit/        # Phase 5: PrivEsc, lateral movement, persistence
│       │   └── README.md
│       ├── reporting/           # Phase 6: Final report, findings, remediation
│       │   └── README.md
│       ├── evidence/            # Screenshots, packet captures, raw output
│       │   └── README.md
│       └── loot/                # Credentials, hashes, exfiltrated data
│           └── README.md
│
├── 📂 templates/                # Reusable templates
│   ├── engagement-scope.md      # Scope definition & authorization checklist
│   ├── report-template.md       # Professional pentest report template
│   └── scan-checklist.md        # Phase-by-phase checklist
│
├── 📂 wordlists/                # Custom wordlists
│   ├── common-dirs.txt
│   └── custom-passwords.txt
│
├── 📂 scripts/                  # Custom automation scripts
│   └── (auto-recon wrappers, etc.)
│
├── 📂 notes/                    # General notes, learning, cheat sheets
│   ├── methodology.md           # Pentest methodology reference
│   ├── tools-cheatsheet.md      # Command references
│   └── networking-basics.md     # Quick networking reference
│
├── 📂 memory/                   # Agent memory (daily logs)
│   └── 2026-03-13.md           # Today's session log
│
├── SOUL.md                      # Agent identity & behavior
├── USER.md                      # About the user
├── IDENTITY.md                  # Agent metadata
├── AGENTS.md                    # Workspace rules
├── TOOLS.md                     # Local tool config
└── HEARTBEAT.md                 # Periodic task config
```

## Naming Convention for New Engagements

```
engagements/<target>-<date>/
```

Examples:
- `raspi5-lab/` — Current lab target
- `acme-webapp-2026-04/` — April web app engagement
- `corp-internal-2026-Q2/` — Internal network assessment

## Agent Output Paths

All pentest agents must write to their engagement directory. **Never create ad-hoc output folders.**

| Agent | Output Path |
|-------|-------------|
| specter-recon | `engagements/<target>/recon/` |
| specter-enum | `engagements/<target>/enum/` |
| specter-vuln | `engagements/<target>/vuln/` |
| specter-exploit | `engagements/<target>/exploit/` |
| specter-post | `engagements/<target>/post-exploit/` |
| specter-report | `engagements/<target>/reporting/` |

The orchestrator specifies `<target>` when spawning each agent (e.g., `raspi5-lab`). Raw evidence (screenshots, pcaps, command output) goes in an `evidence/` subfolder within the phase directory.

## Key Principles

1. **One folder per engagement** — Never mix engagements
2. **Phase-based organization** — Know where everything is
3. **Evidence is sacred** — Never delete raw evidence
4. **Loot is sensitive** — Credentials and hashes stay in loot/
5. **Reports are the product** — Everything feeds into reporting/
