# Pentest Workspace Directory Structure

## Overview

This workspace is organized to support the full penetration testing lifecycle. Each engagement gets its own isolated folder, and shared resources live at the top level.

```
~/.openclaw/workspace/
├── 📂 engagements/              # Each pentest engagement lives here
│   └── pulselink-pi/            # Current target: Raspberry Pi 5 (n-compass TV)
│       ├── recon/               # Phase 1: Passive recon, OSINT, business model, CVE research
│       ├── enum/                # Phase 2: Active enumeration (from physical terminal)
│       ├── vuln/                # Phase 3: Vulnerability analysis (versions, CVEs)
│       ├── exploit/             # Phase 4: Exploitation findings (physical access)
│       ├── report/              # Phase 5: Reports, presentations, guides
│       └── evidence/            # Screenshots, raw output
│
├── 📂 skills/                   # Custom OpenClaw agent skills
│   ├── presentation/            # Generate slide decks from pentest reports
│   ├── pentest-orchestrator/    # Agent workflow with decision gates
│   └── cipher/                  # General programming assistant
│
├── 📂 memory/                   # Agent memory (daily logs)
│   └── 2026-03-17.md            # Today's session log
│
├── SOUL.md                      # Agent identity & behavior
├── USER.md                      # About the user
├── IDENTITY.md                  # Agent metadata
├── AGENTS.md                    # Workspace rules
├── TOOLS.md                     # Local tool config
├── HEARTBEAT.md                 # Periodic task config
├── MEMORY.md                    # Long-term agent memory
└── workspace-structure.md       # This file
```

## Engagement Structure (pulselink-pi)

### What Was Actually Done

The pulselink-pi engagement is based on **physical terminal access** to the Raspberry Pi. No network-based exploitation was performed.

| Phase | Directory | Content | Verified? |
|-------|-----------|---------|-----------|
| Recon | `recon/` | Business model research, CVE databases, attack surface mapping | ✅ Research |
| Enum | `enum/` | nmap scan results, filesystem audit, service enumeration | ✅ Real data |
| Vuln | `vuln/` | CVE verification against confirmed versions, Electron analysis | ✅ Verified |
| Exploit | `exploit/` | Physical terminal command outputs (6 rounds), exploitation plans | ✅ Real terminal output |
| Report | `report/` | Full reports, presentation slides, fix guides | ✅ Based on real findings |

### What Was NOT Done
- Network-based attacks (tcpdump, MQTT broker exploitation) — never executed
- Content injection via MQTT — theoretical only
- Fleet-wide compromise demonstration — not proven

### Terminal Output Evidence

Raw command output from physical terminal access:
- `exploit/pi-terminal-output.txt` (round 1: sudo, system info, SUID, services)
- `exploit/pi-terminal-output-2.txt` (round 2: .env, certs, playlist)
- `exploit/pi-terminal-output-3.txt` (round 3: manifest, CUPS, processes)
- `exploit/pi-terminal-output-4.txt` (round 4: home dir, .config, playlist update)
- `exploit/pi-terminal-output-5.txt` (round 5: journalctl, pulselink service, MQTT logs)
- `exploit/pi-terminal-output-6.txt` (round 6: systemd service, binary strings, Paho MQTT)

## Agent Output Paths

| Agent | Output Path | Notes |
|-------|-------------|-------|
| specter-recon | `engagements/<target>/recon/` | Passive recon, OSINT |
| specter-enum | `engagements/<target>/enum/` | Active scanning |
| specter-vuln | `engagements/<target>/vuln/` | CVE analysis |
| specter-exploit | `engagements/<target>/exploit/` | Exploitation findings |
| specter-report | `engagements/<target>/report/` | Reports + presentations |
| specter-skillcrafter | `skills/<skill-name>/` | Skill creation |

## Skills

| Skill | Path | Purpose |
|-------|------|---------|
| `presentation` | `skills/presentation/` | Generate slide decks from pentest reports |
| `pentest-orchestrator` | `skills/pentest-orchestrator/` | Agent workflow with 7 phases, decision gates, handoff protocol |
| `cipher` | `skills/cipher/` | General programming assistant |

## Git Repository

- **Remote:** https://github.com/duriandurino/openclawrino.git
- **All engagement data committed and pushed**

## Key Principles

1. **One folder per engagement** — Never mix engagements
2. **Phase-based organization** — Recon → Enum → Vuln → Exploit → Report
3. **Terminal outputs are evidence** — Raw Pi command output preserved as .txt
4. **Only real findings documented** — No theoretical attacks in reports
5. **Reports are the product** — Everything feeds into reporting/
6. **Skills are reusable** — Presentations and orchestrator skills work across engagements
