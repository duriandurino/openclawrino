---
name: preengagement-essentials
description: "Methodology and decision framework for the penetration testing pre-engagement phase and Rules of Engagement. Use when: preparing a real pentest, checking authorization, defining scope vs ROE, building safety/communication/data-handling rules, handling third-party/cloud approvals, or deciding whether testing may legally and operationally begin. NOT for: replacing legal counsel, skipping signed permission, or running active testing before engagement controls are in place."
---

# Pre-Engagement Essentials

Use this skill to make real pentest engagements authorized, bounded, and operationally safe before intrusive work begins. This is a **governance and gating layer** for the engagement, not a replacement for legal advice.

## When to Use

✅ **USE this skill when:**
- "Start a real pentest engagement"
- "Can we test this target yet?"
- "What's the difference between scope and ROE?"
- "Help me build the rules of engagement"
- "What approvals do we need before testing?"
- "How do we handle third-party/cloud targets?"
- A pentest task needs authorization/scope/ROE confirmation before active work

## When NOT to Use

❌ **DON'T use this skill when:**
- Legal advice beyond engagement-planning best practice is required
- Active testing is already underway and you are not assessing governance gaps
- Replacing specialized recon/enum/vuln/exploit/post/report phase work
- Treating it as permission to proceed without signed authorization

## Core Rules

1. **No signed permission, no test**
   - Do not start real intrusive testing until authorization is explicit and documented.

2. **Scope and ROE are different**
   - Scope = what / where
   - ROE = how / when / under what constraints

3. **Third-party/cloud boundaries matter**
   - Customer permission may not cover providers, hosted services, or shared infrastructure.
   - Check provider ROE and approval requirements before testing.

4. **Safety must be engineered up front**
   - Define windows, contacts, stop conditions, resume authority, and prohibited activities before testing.

5. **Evidence and data handling start here**
   - Data minimization, encryption, retention, destruction, and reporting expectations belong in pre-engagement, not as an afterthought.

## Pre-Engagement Objectives

Before active work, align on:
- business objectives and success criteria
- scope boundaries and exclusions
- authorization chain and sign-off
- rules of engagement
- communications and emergency handling
- data handling and reporting expectations
- third-party/cloud/provider constraints
- scope change process

## Scope vs ROE

Use this distinction strictly:

### Scope
Defines:
- which targets are in scope
- which targets are out of scope
- which environments/interfaces are covered
- which test types are included or excluded

### Rules of Engagement
Defines:
- when testing is allowed
- how intrusive it may be
- who gets notified and when
- what must stop testing
- how evidence and sensitive data are handled
- how findings are escalated and delivered

## Authorization Gate

Before a real pentest begins, confirm:
```text
Signed permission to test exists
Authorizing party is competent to grant permission
In-scope assets are listed clearly
Out-of-scope assets are listed clearly
Allowed / prohibited actions are explicit
Emergency contacts exist
Data handling rules exist
Reporting expectations exist
```

If any of these are missing, do not proceed as if the engagement is fully authorized.

## Core Artifacts

A defensible engagement should usually have:
- scope statement / SOW
- permission to test / authorization memo
- Rules of Engagement document
- contact and escalation list
- data handling plan
- reporting expectations
- optional provider / third-party approvals

## ROE Minimum Structure

A good ROE should include:
- purpose and parties
- scope reference
- assumptions and limitations
- risks and mitigations
- personnel and contacts
- schedule and safe windows
- source IPs / locations / access paths
- allowed and prohibited activities
- incident handling and stop conditions
- data handling
- reporting and debrief expectations
- cleanup and closeout expectations
- signatures / versioning

## Safety Controls

At minimum, define:
- safe testing windows
- blackout periods
- fragile/legacy system handling
- stop conditions
- resume authority
- emergency communication path
- prohibited actions (e.g. DoS, destructive testing, persistence if not allowed)
- cleanup/disclosure obligations for tester-created artifacts

## Third-Party and Cloud Checks

Before testing hosted or provider-backed assets, confirm:
- who actually owns the asset boundary
- whether a provider policy or cloud ROE applies
- whether written provider approval is needed
- whether shared infrastructure is excluded
- whether source IP restrictions or provider-specific conditions apply

## Change Control

If scope changes mid-engagement:
- do not quietly expand scope
- route through explicit approval/change control
- document newly discovered out-of-scope items as limitations until approved
- update engagement artifacts if scope is formally expanded

## Reporting Expectations

Define before testing:
- interim critical-finding escalation timing
- draft/final report timing
- deliverable formats
- debrief expectations
- retest expectations
- who receives which deliverables

## Data Handling Rules

Set and document:
- what data may be collected
- how to minimize collection
- encryption in transit and at rest
- who may access evidence
- retention duration
- destruction / wipe expectations
- whether written destruction confirmation is required

## Red Flags

Stop and reassess if:
- permission is implied but not signed
- target boundaries are vague
- third-party hosting exists but approvals are unclear
- nobody owns incident/stop decisions
- testing windows are unsafe or unspecified
- prohibited actions are not explicitly listed
- data handling is hand-wavy or absent

## Sub-Agent Guidance

When a pentest sub-agent uses this skill, it should:
- check whether authorization and ROE are actually present before active work
- refuse to assume scope from vague wording
- surface missing approvals or unsafe ambiguity early
- treat provider/third-party boundaries as real constraints
- preserve limitations and scope gaps for reporting

## References

Load on demand:
- `references/examples.md` — trigger phrases and expected use
- `references/authorization-checklist.md` — go/no-go authorization gate
- `references/roe-template.md` — compact ROE structure
- `references/cloud-third-party-checks.md` — hosted environment approval checks
