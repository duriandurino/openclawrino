# Appendix

## Report Prep Notes for specter-report

### Core reporting stance
- This engagement should be reported as an evidence-backed blocked state, not as a failed or abandoned assessment.
- The report should distinguish between validated on-box weaknesses and missing-artifact hypotheses.
- Avoid overstating the effect of the env edit. It helped validate the weakness in the authorization gate, but the deeper blocker was the absence of original Phoenix/runtime provenance.

### Key validated storyline
1. `hardware-lock.env` can be altered locally, weakening the authorization layer.
2. The LUKS-backed `vault.img` remained the effective security boundary.
3. `setup.enc` was recovered and decrypted locally, but it only bootstraps the install chain.
4. The real guarded runtime path depends on second-stage Phoenix artifacts (`phoenix.enc` and `phoenix_install.sh --guard`).
5. Those Phoenix artifacts were not recoverable locally during this engagement.
6. Internal-only recovery on the present box is therefore blocked in an evidence-backed way.

### Do not overclaim
- Do not claim full player recovery or vault compromise.
- Do not claim the original authorized tuple was recovered.
- Do not describe Phoenix behavior beyond what was directly observed from `setup.enc`, repair scripts, and local residue.

### High-value evidence to reference
- EVI-004 through EVI-007 for the authorization gate, unlock path, service chain, and vault failure.
- EVI-008 through EVI-011 for shell-history recovery, repair-loop behavior, package/runtime inspection, and empty runtime placeholders.
- EVI-012 for decrypted `setup.enc` proving the Phoenix second-stage bootstrap chain.
- EVI-013 for the absence of surviving local Phoenix artifacts and lack of an evidence-backed original env rollback source.

- TBD
