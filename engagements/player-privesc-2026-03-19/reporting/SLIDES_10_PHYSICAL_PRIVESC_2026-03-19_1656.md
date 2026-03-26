# Presentation Deck — Player Pentest: Privilege Escalation via Physical Access

**Engagement ID:** PLAYER-PRIVESC-2026-03-19  
**Target:** Player Pentest: Privilege Escalation via Physical Access  
**Audience:** Mixed (Leadership + Technical)  
**Slides:** 10

---

### SLIDE 1: Physical Access to Root — Executive Brief

**Visual:** Title + risk badge (CRITICAL) + attack chain icon

**Content:**
- Assessment proved rapid privilege escalation from local access to root
- Root compromise unlocked sensitive credentials, keys, and operational data
- Encryption controls existed, but key management design failed
- Overall posture for physical adversary: **CRITICAL**

**Speaker Notes:**
This engagement focused on what happens when an attacker gets hands-on access to a Player device. We confirmed privilege escalation to root and full access to protected business data. The key insight: strong crypto alone is not enough if key handling and local hardening are weak.

**Transition:** Next: what was in scope and what assumptions were tested.

---

### SLIDE 2: Problem Statement & Scope

**Visual:** Scope panel (in-scope, assumptions, constraints)

**Content:**
- Objective: validate privilege escalation risk with physical/local access
- In scope: local filesystem, vault unlock path, credential handling, host controls
- Out of scope: destructive operations, denial-of-service, production downtime
- Test lens: can a low-skill attacker move from local access to high-impact compromise?

**Speaker Notes:**
We intentionally modeled a realistic physical-access adversary: someone with brief but direct access to the Player. The goal was not disruption, but proof of impact and attack feasibility.

**Transition:** Next: target architecture and trust boundaries.

---

### SLIDE 3: Target Overview & Trust Boundaries

**Visual:** Simple architecture diagram (Player OS → unlock scripts → encrypted vault → app/db/keys)

**Content:**
- Device: Raspberry Pi Player with local unlock automation
- Protected asset: LUKS2 vault with app data and secrets
- Unlock flow tied passphrase generation to hardware serial logic
- Trust boundary failure: key derivation artifacts accessible from host filesystem

**Speaker Notes:**
The design intent was to bind vault access to device identity. In practice, unlock material and logic were discoverable on the same host, collapsing separation between encrypted data and key path.

**Transition:** Next: concise view of the attack chain.

---

### SLIDE 4: Attack Chain — Physical Access to Root-Level Impact

**Visual:** 4-step flowchart

**Content:**
- Step 1: Obtain local/physical access to Player
- Step 2: Discover unlock scripts and hardware-based key logic
- Step 3: Decrypt/mount protected data and extract secrets
- Step 4: Leverage elevated access + secrets for broader control and impersonation risk

**Speaker Notes:**
No exotic exploit chain was required. The attacker follows deterministic local steps and reaches high-impact outcomes quickly. Attack complexity is low once filesystem access is achieved.

**Transition:** Next: findings summary by severity.

---

### SLIDE 5: Key Findings Summary

**Visual:** Severity matrix table

**Content:**
| # | Finding | Severity |
|---|---------|----------|
| 1 | Privilege escalation path from local access to root-equivalent impact | CRITICAL |
| 2 | Predictable/hardcoded key derivation artifacts | HIGH |
| 3 | Plaintext credential and key exposure post-unlock | HIGH |
| 4 | Weak local hardening enabling rapid attacker progression | HIGH |
| 5 | Insufficient monitoring of sensitive local access events | MEDIUM |

**Speaker Notes:**
The lead issue is not one bug but a chain: weak key handling + local exposure + limited host controls. Combined, these convert short physical access into full compromise potential.

**Transition:** Next: deep dive into the critical finding.

---

### SLIDE 6: Critical Finding — Local Access Enables Privilege Escalation Impact

**Visual:** Critical badge + impact panel

**Content:**
- **Severity:** CRITICAL
- **What:** Local attacker can traverse unlock path and obtain protected data/control
- **Why it matters:** compromise extends beyond one file or process into platform trust
- **Business impact:** data exposure, unauthorized content control, fleet-level abuse potential

**Speaker Notes:**
From a risk perspective, this behaves like privilege escalation: low initial foothold becomes high-privilege control over secrets and operational capability. This is a direct business-risk event, not just a local misconfiguration.

**Transition:** Next: evidence of sensitive material exposure after compromise.

---

### SLIDE 7: Evidence of Post-Compromise Exposure

**Visual:** Evidence inventory list (sanitized)

**Content:**
- Application source and runtime config became accessible
- Operational database contents were exposed
- API keys/license material present in recoverable form
- Additional artifacts (e.g., dumps/logs/history) increased blast radius

**Speaker Notes:**
Once attackers clear the local privilege boundary, they do not just get one secret—they get a collection of reusable artifacts that can enable persistence, impersonation, and lateral abuse.

**Transition:** Next: business impact and likelihood.

---

### SLIDE 8: Business Impact Assessment

**Visual:** Impact heatmap (confidentiality/integrity/availability)

**Content:**
- **Confidentiality:** High risk (credentials, internal data, operational metadata)
- **Integrity:** High risk (potential unauthorized content/control actions)
- **Availability:** Moderate-to-high risk (service disruption possible via control abuse)
- **Likelihood:** Moderate-to-high where physical device exposure exists

**Speaker Notes:**
Even if physical access is considered constrained, exposure across many deployed devices makes probability meaningful. One compromised endpoint can have disproportionate downstream impact.

**Transition:** Next: prioritized remediation plan.

---

### SLIDE 9: Remediation Roadmap (Priority-Ordered)

**Visual:** 30/60/90 day plan

**Content:**
- **Immediate (0–30d):** rotate exposed credentials/keys; remove hardcoded key logic; lock down local privilege paths
- **Near-term (30–60d):** implement hardware-backed secret storage (TPM/secure element), enforce least privilege, strengthen filesystem protections
- **Mid-term (60–90d):** central secret management, host telemetry/audit for local sensitive access, secure build/provisioning controls
- Re-test required after fixes to validate exploit chain closure

**Speaker Notes:**
Start with containment and key rotation, then fix architecture so secrets are never recoverable through local script discovery. Finish by adding detection and governance to prevent regression.

**Transition:** Final takeaway and Q&A.

---

### SLIDE 10: Final Takeaway & Q&A

**Visual:** “Strong Crypto ≠ Strong Security” callout

**Content:**
- Physical-access threat model is currently under-defended
- Root-cause is key management and local trust-boundary design
- Remediation is feasible with phased engineering controls
- Next step: approve remediation sprint + verification retest

**Speaker Notes:**
The important message: this is solvable. We already know the highest-value controls. If we execute the roadmap and retest, we can materially reduce compromise likelihood and blast radius.

**Transition:** Q&A / decision on remediation timeline.
