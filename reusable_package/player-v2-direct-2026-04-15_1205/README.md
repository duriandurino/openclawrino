# Player V2 Direct Pentest Package

## Purpose
This package is a reusable, local-first pentest handoff kit for **authorized assessment of Player V2** devices when the operator has **direct keyboard and mouse access to the Raspberry Pi 5B** and does **not** have SSH credentials or decryption passphrases.

It is designed for:
- the original operator continuing work later
- a junior-to-mid pentester following a guided workflow
- repeatable assessments of similar Player V2 / Phoenix / Hardware Lock style targets

This package focuses on **evidence-first, operator-driven execution**. It does not assume vulnerabilities. It gives you a safe structure for collecting evidence, validating hypotheses, and producing report-ready outputs.

## Authorization reminder
Only use this package for systems you are explicitly authorized to assess and only within the agreed Rules of Engagement.

## Target snapshot
- **Target description:** Player V2
- **Target type:** Raspberry Pi 5B, Electron app, Python service, IoT, encrypted components
- **Entry point:** Direct interactive access on the Raspberry Pi with keyboard and mouse
- **Known constraints:** No SSH, no known passphrases, network posture may be heavily restricted
- **Operator skill level assumed:** Comfortable with basic shell commands and simple scripts
- **Preferred script environment:** Bash
- **Primary related terms in prior evidence:** Phoenix, Hardware Lock, Player V2, Raspi, Electron

## Goal of assessment
**Assumption:** The goal is to assess Player V2 for realistic security weaknesses and document validated attack paths across local access, exposed files, services, application behavior, encryption workflow, and recoverable secrets, while preserving evidence for a professional report.

Adjust `docs/assessment-profile.md` before starting if the engagement goal differs.

## What is already known from prior workspace evidence
This package is grounded in prior evidence and should not start from zero.

### Known network posture from prior work
Previous work against a Player V2 target showed:
- very limited network exposure
- port 111/rpcbind and mDNS only
- SSH rejecting connections rather than allowing them
- no meaningful network traffic captured during passive sniffing
- cloud MQTT requiring TLS and authentication

**Implication:** do not waste too much time on blind network-only attacks if the current target looks similar. Validate quickly, then pivot to direct-on-device work.

### Known local-analysis direction from prior work
Related Player / Hardware Lock work indicates these are high-value areas:
- Electron application files under `/opt` or app resources paths
- Python services and helper scripts
- Phoenix / hardware lock logic
- shell history, service definitions, install/repair scripts
- encrypted artifacts such as `setup.enc`
- credentials or passphrases recoverable from operator artifacts, scripts, or local history

## Folder guide
- `docs/` - runbook, assessment profile, handoff notes, operator quick reference
- `evidence/` - screenshots, copied configs, command output, hashes, recovered artifacts
- `logs/` - command logs and activity logs
- `results/` - normalized outputs, parsed summaries, extracted indicators
- `reports/` - working report files and final markdown report set
- `slides/` - presentation outline and slide content
- `templates/` - reusable report and note templates
- `scripts/` - helper scripts for bootstrap, logging, triage, normalization, and export

## Engagement flow
Follow this order unless the current device condition forces a safer pivot:

1. **Prepare the workspace**
2. **Record scope and assumptions**
3. **Collect baseline evidence from the live device**
4. **Validate current network posture quickly**
5. **Enumerate local application and service surface**
6. **Look for stored credentials, passphrases, and encrypted workflow clues**
7. **Validate findings carefully and avoid destructive changes**
8. **Document evidence continuously**
9. **Write the report as you go**
10. **Export markdown, PDF, and presentation outputs locally**

---

# Step-by-step execution guide

## Step 1 - Bootstrap the package
### Objective
Create the local working structure for this specific run and avoid messy evidence sprawl.

### Run
```bash
bash scripts/00-bootstrap-engagement.sh
```

### Success looks like
- timestamped run directory created under `results/runs/`
- starter logs created
- operator prompted to edit assessment profile if needed

### Save as evidence
- bootstrap log
- chosen run directory name

### If this fails
- check write permissions
- run `pwd` and confirm you are inside this package root
- create `results/runs/manual-<timestamp>/` manually and continue

---

## Step 2 - Review scope, assumptions, and stop conditions
### Objective
Make sure the operator is not freelancing beyond the authorized path.

### Review first
- `docs/assessment-profile.md`
- `docs/handoff-notes.md`
- `templates/evidence-log.md`

### Validate
Confirm these before touching the target:
- the device is in scope
- direct console interaction is allowed
- rebooting, unplugging, storage removal, network disruption, and destructive testing rules are known
- credentials are not to be brute-forced unless explicitly approved

### Stop and ask before continuing if
- the system appears production-critical and downtime rules are unclear
- storage tampering or hardware disassembly would be required
- exploitation would alter ads, data, or live service behavior beyond agreed rules

---

## Step 3 - Capture a live baseline from the device
### Objective
Record what the device is right now before changing anything.

### Run
```bash
bash scripts/10-live-baseline.sh
```

### What it collects
- hostname, user, date/time
- kernel and OS details
- IP addresses and interfaces
- listening services
- mounted filesystems
- running processes of interest
- systemd service names related to player, electron, phoenix, hardware, python, node

### Success looks like
- baseline files written under the current run folder
- command transcript saved to `logs/`

### Save as evidence
- `baseline-system.txt`
- `baseline-network.txt`
- `baseline-processes.txt`
- photos/screenshots of the live UI if relevant

### Decision points
- if the device is clearly a different build than expected, update `docs/assessment-profile.md`
- if the user context already has root or passwordless sudo, log it as a major finding candidate but still verify carefully

---

## Step 4 - Quick network validation, then pivot if minimal
### Objective
Confirm whether the current Player V2 still matches the previously observed hardened network posture.

### Run
From an authorized assessment host on the same network:
```bash
bash scripts/20-network-check.sh <target-ip>
```

### Expected output
- quick port snapshot
- notes on filtered vs rejected services
- service banner capture if any exist

### Success looks like
- you know whether network work is worth deeper effort

### Decision points
- **If only rpcbind/mDNS/minimal exposure appears:** document it, stop deep network poking, pivot local
- **If HTTP/API/SSH/VNC appears:** save banners and continue with targeted enumeration
- **If target is silent:** verify IP/MAC locally from the device before assuming the network is dead

### Save as evidence
- port scan output
- arp/ping evidence
- any banners or refusal messages

---

## Step 5 - Enumerate the local app and service surface
### Objective
Map the actual software attack surface on the Pi itself.

### Run
```bash
bash scripts/30-local-surface-enum.sh
```

### What to focus on
- `/opt/`
- `/home/pi/`
- `/etc/systemd/system/`
- `/lib/systemd/system/`
- Electron resources directories
- Python service code
- Node/Electron startup wrappers
- Phoenix / hardware lock / repair scripts

### Success looks like
- file inventory written to `results/`
- likely app directories identified
- service launch paths mapped

### Evidence to save
- copies or hashes of launch scripts
- service unit files
- directory listings for relevant app paths
- config files with secrets redacted only in public-facing outputs, not in raw evidence

### Decision points
- **If app code is found:** inspect startup flow first, not random files
- **If only placeholders exist:** document them and look for external dependency references
- **If encrypted assets are referenced:** move to Step 6

---

## Step 6 - Hunt for secrets, passphrases, and encryption workflow clues
### Objective
Find recoverable material that explains how encrypted artifacts or hardware lock logic actually work.

### Run
```bash
bash scripts/40-secret-and-artifact-triage.sh
```

### Areas to review manually after script output
- shell history files
- app configs
- environment files
- repair scripts
- installer scripts
- Python source for hardcoded serials or derived keys
- references to `setup.enc`, `vault.img`, `openssl`, `cryptsetup`, `Phoenix`, `hardware_lock`, `serial`, `passphrase`

### Success looks like
- candidate secrets list created
- encrypted artifacts hashed and indexed
- references to decryption or unlock flow identified

### Decision points
- **If a candidate passphrase is found:** validate it in a controlled copy workflow, never against the original first if avoidable
- **If no passphrase is found but workflow references exist:** document the dependency chain and blocked path
- **If an artifact is present but untouched:** hash it and preserve it before testing

### Save as evidence
- command output logs
- artifact hashes
- exact file paths where indicators were found
- screenshots if secrets only appear in UI or history viewers

---

## Step 7 - Validate candidate findings carefully
### Objective
Convert hypotheses into validated findings or blocked paths.

### Use this rule
Do not write "found vulnerability" until you can reproduce it now.

### Example validations
- test whether `sudo -l` gives passwordless elevation
- test whether a recovered passphrase actually decrypts a copied artifact
- test whether a service unit exposes an unsafe script path or writable execution path
- test whether Electron resources reveal hardcoded API endpoints, tokens, or local privilege paths

### Controlled-validation reminders
- prefer copied artifacts over originals
- prefer read-only collection before modification
- avoid reboot unless approved
- record exact commands used and exact result

### Outcome buckets
- **Validated** - reproducible now, evidence captured
- **Observed but not revalidated** - likely true but not confirmed live, do not overstate
- **Blocked path** - useful negative result, include it
- **Inconclusive** - needs missing credential, hardware, or external artifact

---

## Step 8 - Keep the evidence log current
### Objective
Make the report easy later by writing while you work.

### Do this continuously
- append commands and outcomes to `reports/evidence-log.md`
- duplicate candidate findings into `reports/findings.md` only after validation work starts
- track dead ends in `docs/handoff-notes.md`

### Good evidence examples
- exact command
- exact output excerpt
- file path
- hash
- screenshot reference
- date/time
- why it matters

---

## Step 9 - Build the report in parallel with testing
### Objective
Avoid the usual pile of raw notes with no deliverable.

### Fill these files as you go
- `reports/report.md`
- `reports/executive-summary.md`
- `reports/findings.md`
- `reports/remediation.md`
- `reports/evidence-log.md`

### Decision branches
- **No findings:** use the no-findings pathway already included in templates
- **Partial assessment only:** state exactly what blocked deeper work
- **Inconclusive crypto path:** document what artifact exists, what was tested, and what key material is still needed

---

## Step 10 - Export local deliverables
### Objective
Produce clean outputs for handoff and presentation.

### Markdown stays primary
Keep `reports/report.md` as the source of truth.

### Export options
```bash
bash scripts/90-export-md-to-html.sh reports/report.md
python3 scripts/91-build-presentation-outline.py reports/findings.md slides/slides.md
```

If local PDF tooling exists:
```bash
pandoc reports/report.md -o reports/report.pdf
pandoc slides/slides.md -t pptx -o slides/player-v2-presentation.pptx
```

If you want to use existing workspace tooling instead of plain pandoc, review:
- `scripts/pentest_pptx_generator.py`
- `reporting/scripts/generate_report.py`

### Final checks
- findings are evidence-backed
- blocked paths are not written as wins
- remediation is specific
- screenshots and hashes are referenced
- next steps are clear for the next operator

---

## Fast operator checklist
1. Run bootstrap
2. Review scope and stop conditions
3. Capture baseline
4. Validate network quickly
5. Enumerate local surface
6. Triage secrets and encrypted artifacts
7. Validate only what you can prove
8. Write the report while working
9. Export MD/PDF/PPT
10. Leave a clean handoff note
