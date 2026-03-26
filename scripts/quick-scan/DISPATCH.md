# Quick Scan vs Full Pentest — Dispatch Guide

Use this guide to decide whether a target should go through:

- **Quick Scan** — rapid triage / hygiene / exposure assessment
- **Full Pentest** — structured multi-phase engagement with recon → enum → vuln → exploit → reporting

---

## Choose Quick Scan When

Use quick scan if the user wants:

- a **fast check**
- a **quick vulnerability review**
- an **antivirus-like sanity check**
- a **surface-level report**
- a **triage pass before deciding on deeper testing**
- a **safe, low-friction first pass**

### Common phrases that imply Quick Scan
- "quick check"
- "quick scan"
- "scan this webapp"
- "check this API"
- "do a fast review"
- "give me a quick report"
- "just tell me if anything obvious is wrong"

### Recommended quick-scan profiles

| Target type | Profile |
|---|---|
| General website | `webapp` |
| Deeper web triage | `webapp-deep` |
| API | `api` |
| API with auth/docs concern | `api-auth` |
| Generic host | `host` |
| Windows host | `windows-host` |
| Linux host | `linux-host` |
| Generic player / IoT | `player` |
| PulseLink player | `player-pulselink` |
| MQTT / IoT broker surface | `iot-mqtt` |

### Need help choosing a profile?

Use the recommender:

```bash
python3 scripts/quick-scan/recommend_profile.py --hint "windows host with smb and rdp"
```

### Default quick-scan entry point

```bash
python3 scripts/quick-scan/run_quick_scan.py --profile <profile> --target <target>
```

---

## Choose Full Pentest When

Use the pentest orchestrator if the user wants:

- a **real engagement**
- a **full methodology-driven assessment**
- **deep enumeration and vulnerability validation**
- **exploitation**
- **post-exploitation**
- a **formal pentest report**
- help deciding the **next phase** in an ongoing engagement

### Common phrases that imply Full Pentest
- "run a pentest"
- "start an engagement"
- "enumerate then analyze vulnerabilities"
- "try exploitation"
- "what phase should I do next?"
- "generate the real pentest report"
- "continue this target from recon/enum/vuln"

### Default full-pentest entry point

Use `skills/pentest-orchestrator/SKILL.md` and create / continue an `engagements/<target-name>/` workflow.

---

## Decision Rule

If the user intent is ambiguous:

1. **Start with Quick Scan** when they want speed, triage, or uncertainty reduction.
2. **Start with Full Pentest** when they explicitly want depth, methodology, exploitation, or formal engagement structure.
3. If authorization/scope is unclear, do **not** default to aggressive testing.
4. Quick scan can be used as **Phase 0.5** before a full engagement.

---

## Escalation Path

A quick scan can escalate into a full pentest when:

- candidate findings are high-risk
- exposed services justify deeper enumeration
- the user asks for confirmation or exploitation
- the target matters enough to justify a full engagement

Suggested wording:

> Quick scan found enough signal to justify a full pentest workflow. Next step: create an engagement directory and continue with pentest orchestration.

---

## Report Sharing / Export

After a quick scan finishes, export the latest report with:

```bash
python3 scripts/quick-scan/export_quick_report.py --engagement <engagement>
```

This produces shareable formats from the markdown report and can be used before sending or publishing the result elsewhere.

---

## Operator Rule of Thumb

- **Quick Scan = Should we worry?**
- **Full Pentest = How far can we go, prove it, and report it professionally?**
