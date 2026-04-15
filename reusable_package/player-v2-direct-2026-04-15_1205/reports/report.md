# Player V2 Security Assessment Report

## Report metadata
- **Engagement name:** Player V2 direct assessment reusable package
- **Client / owner:** Authorized operator managed engagement
- **Assessment date(s):** Prior evidence from 2026-03-18 through 2026-04-09, package prepared 2026-04-15
- **Operator(s):** Hatless White package handoff, follow-on operator to validate live
- **Target(s):** Player V2 Raspberry Pi 5B target family with Electron, Python service, and encrypted artifact workflow
- **Authorization reference:** Must be confirmed by the live operator before use
- **Assessment type:** Authorized local-first security assessment package and continuation handoff

## Executive summary
This package was built from prior Player V2 and related Hardware Lock evidence so a fresh operator can resume assessment without starting from zero. The most important conclusion from prior work is that the target family appears to reward direct local analysis much more than blind network-first effort.

Earlier evidence established that network exposure was likely minimal, that `setup.enc` is an OpenSSL salted encrypted artifact whose contents could not be independently validated without legitimate decryption knowledge, and that related recovery logic may depend on missing Phoenix or repair artifacts not present on the device. These are meaningful security and operational findings even where they do not produce immediate payload access.

A fresh live run is still required before promoting any package content into final findings for a specific current device. This report should therefore be treated as a prepared assessment baseline plus evidence-backed continuation guidance, not as a claim that the current live target has already been fully revalidated today.

## Scope
- In scope: authorized local console assessment of a Player V2 Raspberry Pi device, quick same-segment network validation, local application and service enumeration, artifact and secret triage, controlled validation of recoverable clues
- Out of scope: destructive testing, unauthorized brute force, undocumented hardware tampering, and unsupported claims of decrypt success without repeatable proof
- Constraints: no SSH assumed, no decryption passphrases initially known, network may be intentionally minimal, and key recovery may depend on artifacts absent from the live box

## Objective
Assess the Player V2 target for realistic, evidence-backed weaknesses across local privilege paths, startup and service trust boundaries, recoverable secrets, and encrypted artifact workflow, while preserving blocked paths and operational dependencies that materially affect risk.

## Methodology
Use only the phases actually performed.
- Preparation of a reusable direct-assessment package from prior evidence
- Network validation from prior evidence and future quick live re-check
- Local system baseline guidance for future live run
- Local application and service enumeration guidance
- Secret and artifact triage guidance grounded in prior setup.enc and Hardware Lock work
- Controlled validation and blocked-path preservation
- Reporting and presentation preparation

## Assessment summary
### Validated findings
- No fresh live findings have been revalidated inside this package yet.
- Prior evidence strongly supports assessment themes around encrypted artifact trust, undocumented recovery dependency, and likely local-first attack surface.

### Blocked or inconclusive paths
- Prior `setup.enc` decrypt attempts did not yield validated plaintext.
- Related Hardware Lock recovery work indicates local placeholders alone were insufficient when external Phoenix or repair material was missing.
- Prior network observations suggested limited exposed services and low return on deeper blind remote probing.

### Positive security observations
- Prior targets in this family appeared to expose very little remotely.
- Encryption was present around installer workflow artifacts, even though independent auditability remained a concern.
- Prior work preserved negative results instead of overstating compromise, improving report integrity.

## Findings overview
See `reports/findings.md` for package-seeded findings and partial-assessment notes.

## Partial assessment pathway
This package intentionally stops short of claiming final per-device findings because a fresh direct run still needs to occur on the current live target.
- What was attempted: prior evidence review, package preparation, direct-assessment workflow construction, and preservation of known high-value paths
- What blocked further progress: the earlier session was interrupted before package reports were fully patched with concrete continuation text, and no new live validation has yet been run inside this package
- What evidence still supports concern: prior setup.enc analysis, prior network posture observations, and related Hardware Lock evidence around missing external payload dependencies
- What is needed to continue safely: direct console access to the live device, confirmation of stop conditions, and controlled collection using the included scripts

## Recommendations summary
- Immediate actions
  - Run the package on the live target and capture a fresh baseline before making any claims
  - Re-check local startup chain and service definitions before spending significant time on remote-only testing
  - Preserve and hash any encrypted or recovery-related artifacts before attempting validation
- Short-term hardening
  - document installer and recovery workflows so artifact trust does not depend on tribal knowledge
  - pair encrypted artifacts with verifiable provenance metadata
  - review service startup permissions and secret exposure paths
- Medium-term architecture or process changes
  - reduce person-dependent decrypt knowledge
  - improve recoverability and auditability of Phoenix or similar second-stage runtime workflows
  - maintain repeatable evidence-first operator runbooks for field recovery and assessment

## Conclusion
The Player V2 direct package is now a usable continuation kit rather than an empty scaffold. Its strongest current value is to steer the next operator toward the highest-yield local evidence paths, preserve known blocked paths honestly, and prevent loss of context from the interrupted session.

## Appendix
- evidence inventory reference: see `reports/evidence-log.md` and `docs/handoff-notes.md`
- hashes: to be captured during live use with `scripts/40-secret-and-artifact-triage.sh`
- screenshots: to be captured during live validation
- command transcript locations: `logs/` and `results/runs/`
