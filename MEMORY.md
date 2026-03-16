# MEMORY.md — Long-Term Memory

## Pentest Target: Raspberry Pi 5B

- **Target type:** Raspberry Pi 5 Model B
- **Network:** Mixed environment — Windows 11 PCs on same network, Raspi as primary target
- **Physical access:** YES — physical penetration testing is in scope (USB attacks, HDMI, GPIO, SD card, power analysis, JTAG/debug interfaces)
- **Storage lock:** The Raspi's storage device (SD card / NVMe) is locked to the device ID — cannot be cloned or imaged on another machine. All storage-level attacks must happen on the device itself.
- **Attack surface includes:** Network (SSH, services, misconfig) + Physical (USB, GPIO, serial, display output, power side-channels)

## Agent Architecture (Active)

| Agent | Model | Role |
|-------|-------|------|
| specter-recon | xploiter/pentester | Passive recon, OSINT, DNS, Shodan |
| specter-enum | xploiter/pentester | Active scanning, nmap, dirbust |
| specter-vuln | xploiter/the-xploiter | Vulnerability analysis, CVE matching |
| specter-exploit | xploiter/the-xploiter | Exploitation, Metasploit |
| specter-post | xploiter/the-xploiter | PrivEsc, lateral movement, persistence |
| specter-report | xploiter/pentester | Report generation |
| specter-skillcrafter | xploiter/pentester | Creates OpenClaw agent skills |

## Reporting Agent Requirements

- Pentest reports MUST include **security enhancement recommendations** for every vulnerability found
- Each finding should have:
  - Vulnerability description
  - Severity (CVSS or Critical/High/Medium/Low)
  - Proof of concept / evidence
  - **Remediation steps with specific actions**
  - **Hardening recommendations** (not just "fix it" — concrete steps)
- Goal: client should finish reading with an action plan, not just a list of problems

## Tools & Environment

- **OS:** Kali Linux
- **AI models:** ollama/xploiter/pentester (1.6GB), ollama/xploiter/the-xploiter (9.2GB)
- **OpenClaw:** Configured with maxSpawnDepth: 2, maxChildrenPerAgent: 5
- **Skillcrafter:** Custom skill authoring tool created (strict validation, example-driven)
- **GitHub repo:** https://github.com/duriandurino/openclawrino.git
