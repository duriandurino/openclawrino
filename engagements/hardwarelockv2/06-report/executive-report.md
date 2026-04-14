# Hardware Lock V2 Executive Summary

**Classification:** Internal / Authorized Assessment  
**Status:** Final  
**Date:** 2026-04-14  
**Target:** hardwareLockV2

## Executive Conclusion

This assessment found a real weakness in Hardware Lock V2, but it did **not** result in full recovery of the protected runtime.

The first authorization layer is too trusting of local configuration. Testing showed that `hardware-lock.env` can be edited so the device appears authorized on current hardware. That means the env-based hardware check should be treated as weak.

However, that weakness did not expose the protected player runtime. The encrypted `vault.img` remained locked, and the expected Phoenix runtime artifacts required for full recovery were not present on the assessed device. In practice, the vault remained the effective security boundary.

## What Was Validated

- Local authorization values can be aligned to current hardware through editable configuration
- The current unlock routine still fails against the real LUKS vault
- Runtime directories exist only as placeholders in the assessed state
- Historical provisioning traces reveal a staged installer chain: `setup.enc` -> `phoenix.enc` -> `phoenix_install.sh --guard`
- The second-stage Phoenix artifacts and a trustworthy original rollback source were not recoverable locally

## Business Meaning

- A local attacker with file-write access may influence the first hardware check
- That alone is not enough to recover or run the protected runtime from the current device state
- Operational resilience is heavily dependent on preserving trusted provisioning artifacts and external recovery material
- Recovery capability currently appears brittle if those artifacts are lost

## Overall Risk Posture

**Overall assessment:** Moderate risk with an important nuance.

The local authorization layer is weak and should not be relied on as a strong security control. But the protected runtime was still not compromised because the encrypted vault and missing Phoenix provenance blocked practical recovery from surviving on-box artifacts alone.

## Priority Recommendations

### Immediate
- Protect `hardware-lock.env` from unauthorized local modification
- Rotate or retire any provisioning secrets exposed in shell history or old bootstrap workflows
- Reduce noisy failed unlock and repair retry behavior

### Short-Term
- Preserve and control trusted provisioning and repair artifacts
- Add integrity checks for unlock logic, runtime trees, and recovery media
- Document the authoritative recovery path and expected artifact chain

### Medium-Term
- Move device binding toward hardware-backed or tamper-evident controls
- Maintain a secure recovery repository for the full Phoenix-plus-player runtime chain
- Build a formal recovery playbook that does not depend on fragile local residue

## Blockers to Full Recovery

The assessment did not recover the full protected runtime because:
- the current vault key derivation did not unlock the real vault
- no valid external `nctv-phoenix` repair source was available
- no local `phoenix.enc`, `phoenix_install.sh`, or extracted Phoenix tree survived
- no evidence-backed original hardware tuple rollback source was recovered

## Recommended Next Engagement

If further recovery is authorized, the next effort should start with trusted external artifacts, not additional blind on-box changes. The most valuable inputs would be:
- original provisioning materials
- a known-good external repair payload
- a sibling working device for artifact comparison
- explicit authorization for offline lab work against `vault.img`

## Bottom Line

Hardware Lock V2’s env-based authorization is weak, but the encrypted vault remained the real control that mattered. The engagement therefore ended in a defensible blocked-state conclusion: first-layer auth can be manipulated, but the protected runtime was not recovered from the surviving local artifacts.
