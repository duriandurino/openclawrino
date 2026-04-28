# Process Overview

**Engagement:** playerv2-phoenix  
**Document Type:** Non-technical pentest process overview  
**Prepared On:** 2026-04-28 16:24 Asia/Manila  
**Audience:** Non-technical stakeholders, project owners, managers  
**Assessment Window:** 2026-04-24 to 2026-05-01  
**Lead Tester:** Adrian C. Alejandrino  

---

## 1. Purpose of This Document

This document explains the `playerv2-phoenix` penetration test in plain language. It is meant to show what was tested, how the assessment progressed, what tools were used, and what was learned, without requiring the reader to interpret highly technical evidence.

Unlike the technical report, this document focuses on the overall testing journey. It shows how the assessment moved from planning, to discovery, to validation, and finally to reporting.

[IMAGE HERE - cover image, target photo, or engagement visual]

---

## 2. Assessment Objective

The objective of this assessment was to evaluate the security posture of the `playerv2-phoenix` environment across its device, local-access, and network-exposed surfaces.

The engagement focused on understanding how the target behaves during startup, restricted states, local console exposure, and limited network reachability. The goal was not only to identify weaknesses, but also to understand whether the device's protections activate early enough and consistently enough to resist realistic attack paths.

In practical terms, this assessment aimed to answer three business-relevant questions:

- Can an attacker learn useful information from the device before it is fully protected?
- Are there local or network-exposed entry points that create avoidable risk?
- Do the existing controls behave reliably enough to protect the target during real startup and lockout conditions?

[IMAGE HERE - target system or environment overview]

---

## 3. Scope in Plain Language

This assessment covered the following in-scope areas for `Player v2 - Phoenix`:

- The `dev-api.n-compass.online` environment
- The physical device under test
- Local console and boot-time behavior
- Limited network-exposed services on the device
- Indicators related to trust checks, lockout flow, and protected storage behavior

In simple terms, the test looked at both the cloud-facing side of the target and the physical device side. This included what could be seen from the network, what could be seen from the console, and what happened during the device's startup and failure states.

[IMAGE HERE - scope diagram or simple device/network layout]

---

## 4. Pentest Process Followed

This assessment followed a structured penetration testing process so the work would stay evidence-based, organized, and easy to explain.

Instead of jumping directly into deep testing, the engagement was approached in stages. Each phase built on the one before it so that later conclusions were based on live observations, not guesses.

[IMAGE HERE - pentest lifecycle overview graphic]

### Phase 0: Pre-Engagement

Before testing began, the engagement reviewed the scope, permissions, goals, and operating boundaries.

At this stage, the project record indicated that the target included web, API, and device or hardware testing surfaces. The engagement wording also suggested broad testing permission for the named target, while still requiring care around higher-impact activities.

This phase mattered because it established that:
- the named target was authorized for assessment
- reconnaissance and active testing could proceed under the documented window
- the engagement should remain cautious around destructive, disruptive, or otherwise high-impact actions
- the assessment needed to remain evidence-first, especially where wording in the rules of engagement was broad but not perfectly specific

This phase provided the operational foundation for the rest of the work.

[IMAGE HERE - pre-engagement checklist, charter, or scope summary]

### Phase 1: Reconnaissance

The reconnaissance phase focused on understanding the target before deeper testing.

During this phase, the assessment gathered early context about:
- the cloud-facing API surface
- the device's visible boot behavior
- the local lockout state
- host and network details exposed through the local console

This early work revealed several important clues. The device exposed a hostname, operating system banner, and network details through its local console. It also showed signs that the primary lockout flow might rely on a hardware-bound trust or secure-storage chain. In addition, the startup sequence briefly exposed intermediate states before the restricted screen fully took over.

One of the most important recon observations was that the device did not move cleanly from power-on to a fully protected state. Instead, there appeared to be a short transitional period where meaningful information and interaction surfaces became visible before the lockout condition reasserted itself.

[IMAGE HERE - early recon observation or boot screen]

### Phase 2: Enumeration

The enumeration phase turned the early observations into a more concrete inventory of what was actually exposed.

On the device side, this included confirming:
- the device IP address
- alternate visible local consoles
- exposed service names tied to the failure state
- the presence of a brief but meaningful `tty1` interaction window

On the network side, this phase confirmed that the target device was reachable and exposed only a small number of services. The confirmed network-visible services were:
- SSH on port 22
- RPC portmapper on port 111 over TCP and UDP
- mDNS on UDP 5353

This was an important result. It suggested that the device was not broadly exposing many remote services, which is positive from a surface-area standpoint. At the same time, the local console observations showed that low network exposure did not automatically mean low overall risk.

Enumeration also strengthened the view that the primary console was part of a contested startup path. During a short-lived window, the assessment observed a temporary `pi@raspberry` shell prompt and runtime messages associated with staged socket interactions before the lockout path took over again.

This phase helped create a clearer picture of the target: sparse from the network, but more interesting and potentially more fragile during local startup and console transitions.

[IMAGE HERE - service discovery result or console exposure]

### Phase 3: Vulnerability Analysis

Once the exposed behaviors were documented, the next step was to analyze what they might mean from a security perspective.

The core question in this phase was not simply whether something looked unusual, but whether it created a realistic opportunity for an attacker.

The assessment considered the following themes:
- whether console access was exposed more broadly than intended
- whether startup protections were activating too late
- whether visible system states revealed sensitive operational details
- whether the difference between the device's final protected state and its early startup state created a timing-based weakness

This phase did not assume that every observation was automatically a confirmed vulnerability. Instead, it translated live observations into focused security hypotheses.

The strongest risk pattern identified at this stage was the possibility that key protective controls, especially those related to hardware or trust validation, were taking effect only after early console and user-interface exposure had already occurred.

[IMAGE HERE - risk analysis note, timing window, or system-state comparison]

### Phase 4: Exploitation or Controlled Validation

In a completed pentest, observed weaknesses must be checked carefully to determine whether they represent real exposure or only theoretical concern.

For `playerv2-phoenix`, this phase would focus on controlled validation of the most meaningful paths identified earlier, including:
- the startup timing window on the primary console
- the practical significance of the transient shell exposure
- whether exposed local consoles provide usable interaction opportunities
- whether the observed trust or lockout sequence can be meaningfully bypassed, delayed, or observed in a way that increases risk

The intent of this phase is not to be reckless. It is to prove impact safely and clearly enough that the client can decide what must be fixed first.

For stakeholder readers, this is the point where the assessment moves from “this looks concerning” to “this has been validated as meaningful risk” or “this needs no further action.”

[IMAGE HERE - validation evidence or controlled test screenshot]

### Phase 5: Post-Exploitation Review

When meaningful access or control is achieved during a pentest, the next question is what that access would allow in practice.

For a device-focused target like `playerv2-phoenix`, this phase would ask:
- what additional visibility or control becomes possible after local access
- whether sensitive configuration, operational logic, or trust information becomes reachable
- whether an attacker could expand their control beyond an initial foothold
- whether the impact remains local or could affect broader workflows, provisioning, or dependent services

This phase matters because business risk is not only about “getting in.” It is also about what becomes possible after access is obtained.

Even in cases where full compromise is not demonstrated, this phase helps explain the practical importance of partial exposure, shell access, or trust-sequence weakness.

[IMAGE HERE - post-exploitation path, impact map, or access review]

### Phase 6: Reporting and Communication

The final phase converts evidence into action.

For this engagement, the reporting phase is intended to produce two companion outputs:
- a detailed technical report for engineering and security readers
- this process overview for stakeholders who need to understand the assessment journey without reading raw technical evidence

This phase exists to:
- summarize what was tested
- explain what was observed
- highlight where risk comes from
- turn technical results into decisions, priorities, and remediation planning

[IMAGE HERE - report package, presentation, or reporting workflow]

---

## 5. Tools Used During the Assessment

The following tools and methods supported the assessment:

### Kali Linux
Used as the primary operator environment for organizing the engagement, running commands, validating observations, and collecting evidence.

Why it matters:
- It provided a stable testing platform
- It supported the network and local validation workflow
- It kept evidence collection centralized

[IMAGE HERE - Kali workspace or terminal overview]

### Nmap
Used to confirm which services were actually reachable on the device over the network.

Why it matters:
- It helped verify the real network attack surface
- It prevented assumptions about which ports were open
- It supported repeated validation when initial local discovery behavior was misleading

[IMAGE HERE - nmap result screenshot]

### Manual Console Observation
Used to inspect boot flow, lockout messages, visible console sessions, transient prompts, and startup-stage behavior.

Why it matters:
- Some of the most important observations were only visible locally
- It helped identify timing-based exposure not obvious from the network side
- It revealed how the device behaves before the lockout state fully stabilizes

[IMAGE HERE - console or boot-stage screenshot]

### Socket and Service Validation
Used to confirm that reachable services were not false positives and to better understand the behavior of SSH, RPC, and related runtime observations.

Why it matters:
- It improved confidence in the service inventory
- It helped distinguish real exposure from scanning artifacts
- It supported a more accurate view of the target's remote posture

[IMAGE HERE - socket validation or service check screenshot]

### Documentation and Evidence Tracking
Used throughout the engagement to capture what was observed, what was validated, and what remained a hypothesis.

Why it matters:
- It kept the assessment grounded in live evidence
- It made later analysis and reporting more reliable
- It reduced the chance of overstating unconfirmed behavior

[IMAGE HERE - notes, evidence tracker, or documentation screenshot]

---

## 6. How the Phases Connect

Each phase in the pentest built on the previous one.

- **Pre-engagement** confirmed scope, permissions, and safe operating boundaries
- **Reconnaissance** established early context about the device and cloud-facing environment
- **Enumeration** confirmed what was actually exposed, both locally and over the network
- **Vulnerability analysis** translated those observations into focused risk hypotheses
- **Exploitation or validation** tests whether the most important hypotheses produce real impact
- **Post-exploitation review** explains what successful access would mean in practice
- **Reporting** converts all of the above into decisions, remediation planning, and stakeholder communication

This structure matters because a reliable pentest should not feel random. It should feel traceable, where each conclusion can be tied back to what was actually observed and validated.

[IMAGE HERE - phase connection flowchart]

---

## 7. What We Observed

The `playerv2-phoenix` assessment produced several meaningful observations that shaped the security picture of the target.

### Positive Observations

- The device exposed a relatively small remote network surface
- SSH access required authentication and did not provide trivial access from the network side
- Follow-up checks did not reveal a large set of hidden remote services during this assessment window

These are good signs because they suggest the target is not broadly open to casual remote probing.

### Risk-Oriented Observations

- Multiple local console sessions were visible in the device's restricted state
- The primary console appeared to expose a short-lived but meaningful interaction window during startup
- A temporary shell prompt was observed before the lockout state resumed
- Boot-stage runtime messages suggested an internal staged workflow on the primary console
- The lockout or hardware-trust process may not be taking effect early enough to prevent all early-stage exposure

These observations matter because they shift attention away from the remote network surface alone and toward the startup and local-access behavior of the device.

[IMAGE HERE - key observation summary graphic or screenshot]

---

## 8. Why These Observations Matter

From a non-technical point of view, the biggest security concern is timing and exposure.

A system may appear secure once it fully settles into its protected state, but if it exposes useful screens, prompts, host details, or interaction opportunities before that protection is fully active, an attacker may still benefit.

This matters because:
- security controls are only strong if they activate before an attacker can take advantage of early behavior
- local and physical exposure can still be high-value even when remote network exposure is limited
- a short timing window may be enough for a skilled attacker to gather information or begin interaction
- inconsistent startup protection can weaken the trustworthiness of the overall device workflow

In other words, the assessment suggests that the target's strongest risks may come from *when* protection takes hold, not only from *what* is exposed after the system has fully settled.

[IMAGE HERE - simple risk explanation visual]

---

## 9. Key Takeaways for Stakeholders

In simple terms, this assessment shows:

- The device appears intentionally limited from the network side, which is a positive design choice
- The more important security questions are happening locally, especially during startup and restricted-state transitions
- Console exposure and timing-based behavior deserve serious attention, even if the final locked state looks controlled
- Security should be measured across the full device lifecycle, not only in the final steady-state screen that users normally see
- The assessment process helped narrow the focus toward the most meaningful risk areas instead of treating every unusual behavior as equally important

[IMAGE HERE - stakeholder summary graphic]

---

## 10. Recommended Next Steps

Based on the completed assessment flow, the following actions are recommended:

1. Review the startup sequence and confirm whether trust checks and hardware-lock protections can be moved earlier in the boot process
2. Reduce or eliminate unnecessary console exposure during restricted or unauthorized states
3. Review whether transient shell prompts, startup-stage messages, and local system details are being exposed before protections are active
4. Validate whether the `tty1` transition window creates a usable attacker opportunity under repeatable conditions
5. Review whether alternate console sessions should remain reachable or visible on production devices
6. Translate confirmed technical findings into engineering tasks with clear verification criteria
7. Re-test the device after hardening changes to confirm that the early-stage exposure has been removed or reduced

[IMAGE HERE - roadmap, checklist, or next-steps visual]

---

## 11. Screenshot Placement Guide

Use the placeholders above to insert visuals later.

Recommended naming style for images during assembly:
- `process-overview-01-cover.png`
- `process-overview-02-target-overview.png`
- `process-overview-03-scope-diagram.png`
- `process-overview-04-pentest-lifecycle.png`
- `process-overview-05-pre-engagement.png`
- `process-overview-06-boot-screen.png`
- `process-overview-07-service-scan.png`
- `process-overview-08-risk-window.png`
- `process-overview-09-validation.png`
- `process-overview-10-post-exploitation.png`
- `process-overview-11-reporting-workflow.png`
- `process-overview-12-kali-workspace.png`
- `process-overview-13-nmap.png`
- `process-overview-14-console-exposure.png`
- `process-overview-15-socket-validation.png`
- `process-overview-16-notes.png`
- `process-overview-17-phase-flowchart.png`
- `process-overview-18-key-observation.png`
- `process-overview-19-risk-visual.png`
- `process-overview-20-stakeholder-summary.png`
- `process-overview-21-next-steps.png`

If an image is not available yet, leave the placeholder line in place so it is easy to find later.

---

## 12. Relationship to the Technical Report

This document is a companion to the technical pentest report.

- The **technical report** contains detailed findings, evidence, validation steps, severity, and remediation guidance.
- This **process overview** explains the engagement in a more visual, stakeholder-friendly, and process-driven format.

Used together, the two documents help different audiences understand the same assessment from the level of detail that fits their role.
