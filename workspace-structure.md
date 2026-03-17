# Pentest Workspace Directory Structure

## Overview

This workspace is organized to support the full penetration testing lifecycle. Each engagement gets its own isolated folder, and shared resources live at the top level.

```
~/.openclaw/workspace/
├── 📂 engagements/              # Each pentest engagement lives here
│   └── pulselink-pi/            # Current target: Raspberry Pi 5 (n-compass TV)
│       ├── recon/               # Phase 1: Passive recon, OSINT, DNS, business model
│       ├── enum/                # Phase 2: Active enumeration (nmap, filesystem)
│       ├── enum-network/        # Phase 2b: Network enumeration (tcpdump, MQTT, TLS)
│       ├── vuln/                # Phase 3: Vulnerability analysis (versions, CVEs)
│       ├── vuln-network/        # Phase 3b: Network vulns (MQTT, TLS, Paho CVEs)
│       ├── exploit/             # Phase 4: Exploitation (sudo, credentials, physical)
│       ├── exploit-network/     # Phase 4b: Network exploitation (MQTT broker, injection)
│       ├── post-exploit/        # Phase 5: Post-exploitation (original)
│       ├── post-exploit-network/# Phase 5b: Post-exploit (fleet compromise, impact)
│       ├── report/              # Phase 6: Reports, presentations, demo guides
│       └── evidence/            # Screenshots, packet captures, raw output
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

### Phase Mapping (Dual Track)

The pulselink-pi engagement has TWO parallel tracks:

| Phase | Physical Track | Network Track |
|-------|---------------|---------------|
| Recon | `recon/` | (same — covers both) |
| Enum | `enum/` (nmap, filesystem) | `enum-network/` (tcpdump, MQTT, TLS) |
| Vuln | `vuln/` (CVEs, versions) | `vuln-network/` (MQTT vulns, Paho CVEs) |
| Exploit | `exploit/` (sudo, creds) | `exploit-network/` (broker exploit, content injection) |
| Post | `post-exploit/` | `post-exploit-network/` (fleet compromise) |
| Report | `report/` (unified) | `report/` (unified) |

### Presentation Files in `report/`

| File | Slides | Purpose |
|------|--------|---------|
| `presentation-5slide-final.md` | 5 | Network attack story + physical what-ifs (requested) |
| `presentation-agent-suggested.md` | 7 | Agent's recommended format |
| `key-takeaways.md` | — | Executive one-pager |
| `demo-flow-guide-jucy.md` | 9 acts | Live demo script |
| `demo-flow-guide.md` | — | Original demo guide |
| `reverse-fix-guide.md` | — | Pi restoration commands |
| `pentest-report-final.md` | — | Full technical report |
| `findings-summary.md` | — | 17 findings table |

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
| specter-enum (network) | `engagements/<target>/enum-network/` | Traffic capture, MQTT |
| specter-vuln | `engagements/<target>/vuln/` | CVE analysis |
| specter-vuln (network) | `engagements/<target>/vuln-network/` | MQTT/TLS vulns |
| specter-exploit | `engagements/<target>/exploit/` | Exploitation |
| specter-exploit (network) | `engagements/<target>/exploit-network/` | MQTT exploitation |
| specter-post | `engagements/<target>/post-exploit-network/` | Fleet compromise |
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
2. **Phase-based organization** — Dual track: physical + network where applicable
3. **Terminal outputs are evidence** — Raw Pi command output preserved as .txt
4. **Presentation-ready** — Report folder contains slides, demo guides, fix guides
5. **Reports are the product** — Everything feeds into reporting/
6. **Skills are reusable** — Presentations and orchestrator skills work across engagements
