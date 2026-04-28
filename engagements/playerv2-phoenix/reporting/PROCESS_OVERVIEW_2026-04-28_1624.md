# Process Overview

**Engagement:** playerv2-phoenix  
**Document Type:** Non-technical pentest process overview  
**Prepared On:** 2026-04-28 16:24 Asia/Manila  
**Audience:** Non-technical stakeholders, project owners, managers  
**Assessment Window:** 2026-04-24 to 2026-05-01  
**Lead Tester:** Adrian C. Alejandrino  

---

## 1. Purpose of This Document

This document shows, in plain language, how the `playerv2-phoenix` pentest was carried out.

Instead of only saying what the final findings were, this overview shows the actual testing flow: what was checked first, what actions were taken on the device, what OpenClaw was asked to help with, what was observed, and how those observations shaped the next step.

It is meant to answer a simple question for non-technical readers:

**What did the tester actually do, and what did that process reveal?**

[IMAGE HERE - cover image, target photo, or engagement visual]

---

## 2. Assessment Objective

The objective of this assessment was to evaluate the security posture of `playerv2-phoenix` across both its cloud-facing and device-side surfaces.

The main focus of the engagement was the gap between the device's intended protected state and its real startup behavior. In particular, the assessment aimed to determine whether the device exposed useful information, interaction opportunities, or weak transition states before its lockout and trust controls fully took effect.

The test also aimed to answer the following practical questions:

- What can be learned from the device before it settles into its restricted state?
- What network-visible services are actually reachable from the same environment?
- Do the device's local controls activate early enough to prevent abuse during boot and failure states?

[IMAGE HERE - target system or environment overview]

---

## 3. Scope in Plain Language

This engagement covered the following in-scope surfaces for `Player v2 - Phoenix`:

- `https://dev-api.n-compass.online`
- the Raspberry Pi player device under test
- local console behavior
- boot and lockout behavior
- network-exposed services on the local device
- clues related to trust validation, secure-storage flow, and restricted-state handling

In plain terms, this meant the pentest looked at both:
- what the cloud-facing side exposed
- what the physical player device exposed during real interaction

[IMAGE HERE - scope diagram or simple device/network layout]

---

## 4. Pentest Process Followed

This assessment followed the normal pentest flow used in this workspace:

1. Pre-Engagement  
2. Reconnaissance  
3. Enumeration  
4. Vulnerability Analysis  
5. Exploitation or Controlled Validation  
6. Post-Exploitation Review  
7. Reporting  

The value of this structure is that each phase explains why the next one happened.

[IMAGE HERE - pentest lifecycle overview graphic]

### Phase 0: Pre-Engagement

Before touching the target, the testing scope and available authorization notes were reviewed.

The engagement record identified `Player v2 - Phoenix` as the target and listed web, API, and device or hardware testing as in scope. The current form language suggested broad testing permission, but some safety and escalation details were still incomplete, so the practical approach was to proceed carefully and favor low-risk, evidence-first work early on.

At this stage, the tester used OpenClaw's help to organize the engagement materials, confirm what was clearly in scope, and preserve a rules-of-engagement interpretation before deeper testing continued.

What this phase established:
- target name: `Player v2 - Phoenix`
- explicit cloud-facing target: `https://dev-api.n-compass.online`
- selected surfaces: web application, API, device or hardware or IoT
- testing window: 2026-04-24 to 2026-05-01
- working posture: proceed, but stay conservative around high-impact actions

[IMAGE HERE - pre-engagement checklist, charter, or scope summary]

### Phase 1: Reconnaissance

Once scope was accepted, reconnaissance began.

This phase started with simple observation rather than aggressive testing. The tester physically interacted with the player, watched the boot process, and checked what the screen and local consoles revealed before trying deeper actions.

During this stage, the following operator actions were important:
- observed the device's restricted or wrong-device state directly
- switched virtual consoles to see whether the lockout screen fully isolated the system
- watched the startup sequence for timing gaps
- pressed keys during boot to see whether the normal path could be interrupted
- asked OpenClaw to help organize and interpret the growing set of observations

Important live observations from recon included:
- hostname exposed locally: `raspberry`
- operating system banner exposed locally: `Debian GNU/Linux 13`
- IPv4 address exposed locally: `192.168.1.70`
- link-local IPv6 observed: `fe80::2ecf:67ff:fe04:bd1`
- visible alternate console sessions included `tty2` and `tty3`
- failure-state references included `hardware-check.service` and `vault-mount.service`

A particularly important step in this phase was testing the boot interaction window.

During early startup, pressing **F1** exposed a boot-text path showing:
- `Progress: Trying boot mode SD`

The same early window also briefly exposed a GUI-like environment before the restricted state returned.

The tester also relayed this observation to the client early, because it suggested a real startup-order issue rather than a cosmetic display artifact.

Another physical observation worth noting was that **Ctrl+Alt+Esc** appeared to power off or shut down the player, although that behavior was still treated cautiously until repeated validation could confirm whether it was a full shutdown, a display effect, or a watchdog-related behavior.

At the end of reconnaissance, the working theory was already becoming clear: the device appeared to expose useful state too early, before the final lockout behavior fully took over.

[IMAGE HERE - early recon observation or boot screen]

### Phase 2: Enumeration

Enumeration began after reconnaissance established that the device and API were worth deeper inspection.

This phase was where the tester moved from “what seems visible” to “what is actually exposed and repeatable.”

#### Device-side enumeration

The tester used the local console observations as starting points and then validated them through repeatable checks.

Concrete local observations that carried into enumeration included:
- device hostname: `raspberry`
- device IPv4: `192.168.1.70`
- device link-local IPv6: `fe80::2ecf:67ff:fe04:bd1`
- visible login consoles: `tty2` and `tty3` with `raspberry login:`
- transient `tty1` shell prompt: `pi@raspberry`
- boot-stage messages:
  - `Completed socket interaction for boot stage config`
  - `Completed socket interaction for boot stage final`

The tester did not just note that a shell prompt existed. The process specifically captured that the prompt was only visible briefly before the wrong-device or lockout path took back control of the main console.

That detail matters because it changed the question from “is there a login prompt?” to “is there a race window during which the device is not yet fully protected?”

#### Network enumeration

The tester then checked what could actually be reached from the operator environment.

Using Nmap and follow-up validation, the confirmed device-side network inventory became:
- `22/tcp` , `OpenSSH 10.0p2 Debian 7+deb13u2`
- `111/tcp` , `rpcbind`
- `111/udp` , `rpcbind`
- `5353/udp` , `mDNS / Zeroconf`

Additional checks helped remove false leads:
- `137/udp` was revalidated as closed
- `1900/udp` was revalidated as closed
- `123/udp` initially looked `open|filtered` in a fast pass, but later validated as closed

A useful lesson from this phase was that local-subnet discovery behaved inconsistently at first. Normal Nmap discovery suggested the host was down until the tester switched to:
- `-Pn -n --disable-arp-ping`

That adjustment mattered because it prevented the engagement from missing a live target based on misleading local discovery behavior.

The tester also confirmed through manual socket validation that:
- `22/tcp` was accepting connections
- `111/tcp` was accepting connections

#### API-side enumeration

Parallel checks against the cloud-facing side showed that `dev-api.n-compass.online` was live behind AWS infrastructure.

The following concrete observations were gathered:
- public AWS addresses observed: `54.210.39.233` and `54.205.199.192`
- HTTP body observed at simple paths: `This is N-Compass TV.`
- load balancer header: `Server: awselb/2.0`
- backend clue from selected paths: `Server: Kestrel`
- TLS certificate subject: `CN=n-compass.online`

This was useful because it showed that the API side existed and responded consistently, even if its public-facing surface remained intentionally thin.

By the end of enumeration, the picture was much sharper:
- the device had a **small remote network surface**
- the cloud endpoint had a **minimal front-facing presence**
- the most interesting exposure was still on the **local startup and console side**

[IMAGE HERE - service discovery result or console exposure]

### Phase 3: Vulnerability Analysis

At this phase, the tester stopped collecting surface details and started asking what those details meant.

The analysis was driven by the evidence gathered in recon and enumeration, not by assumptions.

The main questions were:
- Why is the device showing host and network details in a restricted state?
- Why can alternate consoles still be reached when the device is supposed to be locked?
- Why does `tty1` briefly show a usable shell prompt before the restricted state resumes?
- Why do staged socket messages appear on the primary console during boot?
- Is the hardware-check or trust path activating too late in the startup order?

At this stage, the strongest working theory became:
- the device's trust or hardware-check protections may be loading **after** early user-facing exposure has already happened

That is a much more concrete statement than simply saying “there may be a timing issue.” It ties the concern directly to what the tester actually observed: boot interruption, transient GUI exposure, transient shell exposure, visible console sessions, and lockout behavior that appeared late rather than immediate.

Because this engagement is still early in the full lifecycle, vulnerability analysis at this point is best understood as a narrowing process. It does not try to force a final finding too early. Instead, it identifies the most credible attack paths worth validating next.

[IMAGE HERE - risk analysis note, timing window, or system-state comparison]

### Phase 4: Exploitation or Controlled Validation

This phase is where the next round of work would prove whether the observed exposure becomes a practical weakness.

For `playerv2-phoenix`, the most likely validation tasks are now clear because recon and enumeration already narrowed them down.

Likely next validation tasks:
- repeat the **F1 during boot** interaction to classify exactly what becomes reachable
- measure how often the transient `pi@raspberry` shell prompt appears and how long it remains interactive
- determine whether alternate consoles are only visible or are actually usable
- test whether the startup race can be reproduced consistently enough to create meaningful attacker opportunity
- test whether the lockout sequence can be delayed, bypassed, or observed in a way that increases exposure

This section is intentionally concrete because it should reflect what the pentest process would actually do next, not just what pentesting usually means in theory.

[IMAGE HERE - validation evidence or controlled test screenshot]

### Phase 5: Post-Exploitation Review

If the validation phase proves that a shell, console, or trust-sequence weakness can be used meaningfully, the post-exploitation phase would ask what that access allows.

For this target, the follow-up questions would include:
- does local access reveal additional configuration or trust logic?
- can an attacker learn more about how the device authorizes itself?
- can any protected storage or protected workflows be observed more directly?
- does the device expose operational details that help future access attempts?

This phase is not about adding drama. It is about measuring impact after an initial foothold is proven.

[IMAGE HERE - post-exploitation path, impact map, or access review]

### Phase 6: Reporting and Communication

The final reporting phase turns the engagement into outputs that different readers can use.

For this engagement, the technical report would carry the deeper evidence, reproduction notes, and remediation detail.

This process overview serves a different purpose. It is meant to show the path of the assessment itself, including:
- what the tester physically did
- what the tester checked on the network
- what OpenClaw was asked to help analyze or organize
- what was actually observed in each phase
- why the next phase became necessary

That is the main value of this document. It gives the reader the story of the pentest, not just the final list of findings.

[IMAGE HERE - report package, presentation, or reporting workflow]

---

## 5. Tools Used During the Assessment

The following tools and methods supported the assessment.

### Physical Interaction with the Device
The tester directly observed the target screen, changed consoles, and interacted with the keyboard during boot.

Examples of actions taken:
- switched to alternate TTY consoles
- pressed **F1** during early startup
- observed lockout, wrong-device, and startup-stage transitions
- noted behavior associated with **Ctrl+Alt+Esc**

[IMAGE HERE - physical interaction or keyboard/console screenshot]

### OpenClaw Assistance
OpenClaw was used as an orchestration and analysis assistant during the engagement.

Examples of assistance requested:
- organize engagement phases
- preserve recon and enum summaries
- help compare live observations with likely trust-path explanations
- help draft reporting outputs from the engagement data

[IMAGE HERE - OpenClaw assistance or workflow screenshot]

### Kali Linux
Used as the main operator environment for running commands and collecting evidence.

[IMAGE HERE - Kali workspace or terminal overview]

### Nmap
Used to validate the live network-visible surface of the device.

Concrete outputs confirmed through this process included:
- `22/tcp` open
- `111/tcp` open
- `111/udp` open
- `5353/udp` open

[IMAGE HERE - nmap result screenshot]

### Manual Socket and Service Validation
Used to confirm that open ports and runtime behavior were real, not just scan artifacts.

[IMAGE HERE - socket validation or service check screenshot]

### Documentation and Evidence Tracking
Used throughout the engagement so that each observation could be tied to a phase and revisited later.

[IMAGE HERE - notes, evidence tracker, or documentation screenshot]

---

## 6. How the Phases Connect

This engagement followed a real chain of logic:

- pre-engagement confirmed it was safe to begin
- recon showed that the device exposed more local detail than expected
- enum proved the device was live at `192.168.1.70` and confirmed the exposed remote services
- vuln analysis reframed those observations into a timing and trust-path problem
- validation planning then focused on the boot race, transient shell, and console usability questions

That phase flow is the core of this document. Each step happened because of the evidence from the step before it.

[IMAGE HERE - phase connection flowchart]

---

## 7. What We Observed

By the current stage of the engagement, the following observations had already been made.

### Device-side observations
- hostname shown locally: `raspberry`
- OS banner shown locally: `Debian GNU/Linux 13`
- IPv4 shown locally: `192.168.1.70`
- IPv6 link-local shown locally: `fe80::2ecf:67ff:fe04:bd1`
- `tty2` and `tty3` showed `raspberry login:`
- `tty1` briefly showed `pi@raspberry`
- boot-stage messages included:
  - `Completed socket interaction for boot stage config`
  - `Completed socket interaction for boot stage final`

### Network-side observations
- `22/tcp` exposed `OpenSSH 10.0p2 Debian 7+deb13u2`
- `111/tcp` and `111/udp` exposed `rpcbind`
- `5353/udp` exposed `mDNS / Zeroconf`
- no broader high-volume service exposure was confirmed from the network side in this phase

### Cloud/API observations
- `dev-api.n-compass.online` responded behind AWS infrastructure
- observed ELB header: `Server: awselb/2.0`
- selected API paths returned `404 Not Found` with `Server: Kestrel`
- root-like paths returned: `This is N-Compass TV.`

### Process observations
- pressing **F1** during startup exposed `Progress: Trying boot mode SD`
- the same early window briefly exposed a GUI-like state before the restricted state resumed
- OpenClaw was asked to help preserve and interpret these observations as the engagement progressed

[IMAGE HERE - key observation summary graphic or screenshot]

---

## 8. Why These Observations Matter

The important issue is not just that something was visible. The issue is **what became visible before protection fully took over**.

The current process suggests three concrete areas of concern:
- the device reveals host and network details in a restricted state
- alternate consoles remain visible during lockout conditions
- the primary console may briefly expose a real interaction window before the trust path fully reasserts control

That combination makes the startup path more important than the final steady-state screen.

[IMAGE HERE - simple risk explanation visual]

---

## 9. Key Takeaways for Stakeholders

At the current stage of the engagement, the practical takeaways are:

- the device is not broadly exposed on the network, which is good
- the more meaningful security questions are happening locally on the device itself
- startup behavior currently looks more interesting than the final locked state
- the pentest is successfully narrowing the problem toward a specific timing and trust-path concern instead of chasing random possibilities

[IMAGE HERE - stakeholder summary graphic]

---

## 10. Recommended Next Steps

Based on the work completed so far, the next actions are:

1. repeat and measure the **F1 boot interaction** window
2. re-check the transient `pi@raspberry` shell prompt for usability and timing
3. determine whether `tty2` and `tty3` are only visible or meaningfully usable
4. inspect whether `hardware-check.service` appears to start too late in the boot sequence
5. continue documenting each repeatable state transition with screenshots and timestamps
6. convert validated behavior into formal findings only after controlled confirmation

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
- `process-overview-12-physical-interaction.png`
- `process-overview-13-openclaw-assist.png`
- `process-overview-14-kali-workspace.png`
- `process-overview-15-nmap.png`
- `process-overview-16-socket-validation.png`
- `process-overview-17-notes.png`
- `process-overview-18-phase-flowchart.png`
- `process-overview-19-key-observation.png`
- `process-overview-20-risk-visual.png`
- `process-overview-21-stakeholder-summary.png`
- `process-overview-22-next-steps.png`

If an image is not available yet, leave the placeholder line in place so it is easy to find later.

---

## 12. Relationship to the Technical Report

This document is a companion to the technical pentest report.

- The technical report gives the detailed evidence, validation logic, and remediation guidance.
- This process overview shows the human-readable testing journey, including what was done and what was seen along the way.

Together, they answer both questions a client usually has:
- **What exactly did you find?**
- **What exactly did you do to reach that conclusion?**
