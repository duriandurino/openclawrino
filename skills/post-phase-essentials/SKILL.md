---
name: post-phase-essentials
description: "Methodology and decision framework for the penetration testing post-exploitation phase. Use when: structuring post-exploitation after a foothold, assessing privilege/data/lateral-movement impact safely, deciding how much evidence is enough, relating behaviors to ATT&CK-style tactics and telemetry, or reinforcing cleanup/reporting discipline after access is gained. NOT for: obtaining initial access, replacing the specialized post skill's concrete actions, or for unauthorized persistence, credential theft, or log tampering guidance."
---

# Post-Exploitation Phase Essentials

Use this skill to make post-exploitation evidence-backed, defender-aware, and tightly scoped. This is a **methodology layer** for the post-exploitation phase, not a replacement for concrete post-access tooling.

## When to Use

✅ **USE this skill when:**
- "Do post-exploitation safely and methodically"
- "We have a shell — what now?"
- "What is the goal of post-exploitation in a pentest?"
- "How much proof is enough after initial access?"
- "How should I assess lateral movement or persistence safely?"
- "What telemetry should defenders see from these actions?"
- A sub-agent needs stronger post-exploitation discipline before acting

## When NOT to Use

❌ **DON'T use this skill when:**
- Still trying to gain initial access → use `exploit`
- Still validating vulnerabilities → use `vuln`
- Teaching broad whole-pentest methodology → use `pentest-essentials`
- Writing only the final report → use `reporting`
- Replacing the specialist `post` skill’s concrete phase work
- Seeking instructions for unauthorized persistence, credential theft, exfiltration, or log tampering

## Core Rules

1. **Post-exploitation measures value, not ego**
   - The goal is to assess what the foothold is worth.
   - Prefer evidence of reachable impact over sprawling activity.

2. **Minimum necessary impact**
   - Demonstrate access and risk with the least disruption possible.
   - Proof-of-access is usually more valuable than collecting large volumes of sensitive data.

3. **Defender relevance matters**
   - Tie behaviors to ATT&CK-style tactic families and likely telemetry.
   - Good post-exploitation findings help defenders understand what to detect and harden.

4. **Scope still rules after access**
   - A shell is not blanket permission.
   - Lateral movement, persistence, and exfiltration proofs must stay inside ROE and stop conditions.

5. **Cleanup is restoration, not concealment**
   - Remove agreed tester-introduced artifacts.
   - Never hide activity or tamper with logs to erase evidence.

## Phase Objectives

After foothold, organize work around:
- privilege assessment / access enhancement
- credential and secret exposure assessment
- local and network discovery
- lateral movement feasibility
- persistence risk assessment (if in scope)
- collection / exfiltration proof-of-access
- cleanup, residual risk, and reporting

## Workflow

Follow this order:
1. confirm ROE, timing, stop conditions, and allowed post-exploitation activities
2. stabilize and document current access context
3. orient locally: user, groups, privileges, reachable resources
4. assess value: what data, systems, and trust paths are reachable?
5. evaluate escalation, credential exposure, and lateral options in least-invasive order
6. prove impact with minimum necessary actions
7. document artifacts, telemetry implications, and cleanup needs
8. produce access-path and residual-risk notes for reporting

## Access Context Record

Before deeper activity, record:
```text
Host / asset
Current user / privilege level
Session type
Network position / reachable segments
High-value local resources visible
Likely trust relationships
Allowed next actions under ROE
```

## Capability Areas

### Privilege Assessment
Goal:
- understand whether the current foothold can become more valuable

Evidence to capture:
- current privilege level
- relevant group/role membership
- local protections and constraints observed
- whether escalation was attempted, blocked, or achieved

### Credential and Secret Exposure
Goal:
- determine whether reusable authentication material or sensitive secrets are exposed

Evidence to capture:
- what category of credential/secret was reachable
- where it was found conceptually
- what systems/accounts it could affect
- mitigation relevance

### Discovery and Collection
Goal:
- identify what sensitive data or important systems are reachable from the foothold

Evidence to capture:
- files/shares/services of interest
- proof-of-access rather than bulk collection
- business value of what was reachable

### Lateral Movement Feasibility
Goal:
- determine whether the foothold expands beyond the initial host

Evidence to capture:
- reachable hosts or trust paths
- what access boundary would be crossed
- whether movement was merely feasible, partially validated, or achieved

### Persistence Risk
Goal:
- assess how an attacker could retain access if not explicitly prevented

Evidence to capture:
- what persistence classes would be plausible in this environment
- whether any were validated under scope
- what defenders should monitor or harden

### Exfiltration Proof-of-Access
Goal:
- prove that valuable data could leave the boundary without actually stealing more than necessary

Evidence to capture:
- what data category could leave
- what channel would make that feasible
- what minimal proof was used
- what controls should have stopped it

## Telemetry and Defender Relevance

Post-exploitation findings should mention likely defender visibility such as:
- Windows security logon / privilege / process events
- Sysmon process, network, registry, and process-access chains
- Linux auditd and auth/syslog traces
- centralized log-management gaps

Rule:
- translate actions into what defenders should have seen
- connect technical impact to monitoring and hardening recommendations

## Impact Ladder

Use the least disruptive proof that still demonstrates value:
1. observation only
2. proof-of-access to non-sensitive marker data or metadata
3. constrained proof of reachable sensitive data
4. limited multi-host or trust-boundary proof
5. broader impact only if explicitly justified and authorized

If a lower rung proves the point, stop there.

## Evidence Standards

Capture:
```text
Initial foothold context
What objective was being assessed
What was observed or proven
Why it matters to the business or defender
What artifacts or telemetry it likely produced
What tester-created changes occurred
Cleanup performed
Residual risk remaining
```

## Access Path Reporting

A strong post-exploitation handoff should describe the path, not just isolated facts:
```text
Initial foothold -> privilege/value gained -> trust boundary crossed -> impact demonstrated -> cleanup state
```

This makes the report useful for remediation and retesting.

## Anti-Patterns

Avoid:
- wandering after getting a shell without a clear objective
- collecting more sensitive data than needed for proof
- treating persistence as default behavior instead of scoped validation
- lateral movement without explicit scope and stop conditions
- deleting or clearing logs as "cleanup"
- reporting access without explaining business value or defender relevance

## Sub-Agent Guidance

When a pentest sub-agent uses this skill, it should:
- keep post-exploitation tied to business impact
- prefer proof-of-access over maximal data handling
- record likely telemetry and artifacts for defenders
- document trust paths and access paths clearly
- separate feasible, validated, and achieved outcomes precisely

## References

Load on demand:
- `references/examples.md` — trigger phrases and expected use
- `references/access-path-template.md` — clean access-path writeup structure
- `references/evidence-checklist.md` — minimum post-exploitation evidence checklist
- `references/telemetry-notes.md` — defender-facing telemetry categories to mention
