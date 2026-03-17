# Slide Visual Templates

## Title Slide

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║            🔒 PENETRATION TEST REPORT                   ║
║                                                          ║
║         PulseLink Digital Signage (n-compass TV)         ║
║         Raspberry Pi 5 — n-compass.online                ║
║                                                          ║
║         Presented by: The Darkhorse                      ║
║         Date: YYYY-MM-DD                                 ║
║         Framework: OpenClaw Specter                      ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

## Problem Statement Slide

```
┌──────────────────────────────────────────────────────────┐
│  THE PROBLEM                                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Digital signage devices are deployed everywhere:        │
│  offices, retail, hotels, hospitals, public spaces       │
│                                                          │
│  ⚠️  They run full OS                                    │
│  ⚠️  Rarely patched or monitored                         │
│  ⚠️  Connected to cloud for content updates              │
│  ⚠️  Default configurations often left unchanged         │
│                                                          │
│  One compromised device = fleet-wide risk                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Target Overview Slide

```
┌──────────────────────────────────────────────────────────┐
│  TARGET PROFILE                                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Device:     Raspberry Pi 5 Model B (4GB)                │
│  OS:         Debian 13 (trixie)                          │
│  App:        PulseLink (nctv-player) v2.0.0              │
│  Runtime:    Electron 35.4.0 / Chromium 134              │
│  Network:    WiFi (192.168.0.125)                        │
│  Access:     Physical keyboard + mouse                   │
│  SD Card:    LOCKED to device (no offline imaging)       │
│                                                          │
│  Business:   n-compass TV ad network                     │
│  Model:      NTV → Dealers → Hosts → Players             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Finding Slide (Single)

```
┌──────────────────────────────────────────────────────────┐
│  🔴 FINDING 1: sudo NOPASSWD Misconfiguration            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Severity: CRITICAL (CVSS 10.0)                          │
│  Affected: pi user on Raspberry Pi                       │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ pi@raspberry:~ $ sudo su                          │  │
│  │ root@raspberry:/# id                              │  │
│  │ uid=0(root) gid=0(root) groups=0(root)            │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  • Instant root with NO password                         │
│  • No exploit required — just "sudo su"                  │
│  • Any physical access = full system compromise          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Findings Summary Table Slide

```
┌──────────────────────────────────────────────────────────┐
│  KEY FINDINGS                                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  #  │ Finding                        │ Severity          │
│  ───┼────────────────────────────────┼──────────────     │
│  1  │ sudo NOPASSWD misconfiguration │ 🔴 CRITICAL 10.0 │
│  2  │ World-readable private key     │ 🔴 CRITICAL 8.8  │
│  3  │ MQTT broker exposure           │ 🟠 HIGH 8.0      │
│  4  │ Content injection risk         │ 🟠 HIGH 7.5      │
│  5  │ Electron zero-days             │ 🟠 HIGH 8.8      │
│  6  │ Fleet-wide MQTT control        │ 🔴 CRITICAL 9.5  │
│                                                          │
│  Total: 15 findings | 5 Critical | 5 High | 5 Med/Low   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Attack Chain Slide

```
┌──────────────────────────────────────────────────────────┐
│  ATTACK CHAIN                                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  PHYSICAL ACCESS                                         │
│       │                                                  │
│       ▼                                                  │
│  ┌─────────┐     ┌──────────┐     ┌─────────────────┐   │
│  │ sudo su │ ──▶ │ root     │ ──▶ │ Extract .env    │   │
│  │ (0 sec) │     │ shell    │     │ + TLS keys      │   │
│  └─────────┘     └──────────┘     └─────────────────┘   │
│                                           │              │
│       ┌───────────────────────────────────┘              │
│       ▼                                                  │
│  ┌──────────────────┐     ┌──────────────────────────┐   │
│  │ Impersonate      │ ──▶ │ Fleet-wide content       │   │
│  │ device to MQTT   │     │ injection via broker     │   │
│  └──────────────────┘     └──────────────────────────┘   │
│                                                          │
│  TIME TO ROOT: < 1 second (2 commands)                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Remediation Slide

```
┌──────────────────────────────────────────────────────────┐
│  REMEDIATION — All fixes under 3 hours                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  P0 — IMMEDIATE (< 10 min each)                          │
│  ☐ Remove NOPASSWD from sudoers                         │
│  ☐ chmod 600 on private key                             │
│  ☐ Move .env to secrets management                      │
│                                                          │
│  P1 — THIS WEEK                                         │
│  ☐ Upgrade sudo to 1.9.17p1+                            │
│  ☐ Run PulseLink as non-root user                       │
│  ☐ Update Electron/Chromium runtime                     │
│  ☐ Restrict playlist directory perms                    │
│                                                          │
│  P2 — THIS MONTH                                        │
│  ☐ Device attestation for MQTT                          │
│  ☐ SSH key auth + disable password auth                 │
│  ☐ Signed content manifests                             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Methodology / Why OpenClaw Slide

```
┌──────────────────────────────────────────────────────────┐
│  WHY OPENCLAW                                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │  RECON      │   │  ENUM       │   │  VULN       │    │
│  │  Agent      │──▶│  Agent      │──▶│  Agent      │    │
│  │  (Research) │   │  (Scan)     │   │  (Analyze)  │    │
│  └─────────────┘   └─────────────┘   └─────────────┘    │
│         │                                    │           │
│         │           ┌─────────────┐          │           │
│         │           │  EXPLOIT    │          │           │
│         └──────────▶│  Agent      │◀─────────┘           │
│                     │  (Attack)   │                       │
│                     └─────────────┘                       │
│                                                          │
│  • 6 agents running in parallel                          │
│  • 3 minutes to root access                              │
│  • 1,174+ lines of auto-generated documentation          │
│  • Live CVE research via web search                      │
│  • Scalable to ANY target                                │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## Q&A Slide

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                      QUESTIONS?                          ║
║                                                          ║
║         Presented by: The Darkhorse                      ║
║         Framework: OpenClaw Specter                      ║
║         Contact: [your contact info]                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

## Severity Color Legend

| Severity | Badge | Usage |
|----------|-------|-------|
| CRITICAL | 🔴 | System compromise, RCE, full access |
| HIGH | 🟠 | Privilege escalation, significant exposure |
| MEDIUM | 🟡 | Limited impact, requires conditions |
| LOW | 🟢 | Info disclosure, defense-in-depth gaps |
| INFO | 🔵 | Observations, recommendations |
