# Appendix

## Report Prep Notes for specter-report

### Core reporting stance
- This engagement is reported as an evidence-backed blocked state, not as a failed or abandoned assessment.
- Validated findings are separated from counterfactual or unmodified-state hypotheses.
- The env edit demonstrated a real weakness in the authorization layer, but it did not defeat the effective cryptographic boundary.

### Core validated storyline
1. `hardware-lock.env` can be altered locally, weakening the first authorization gate.
2. The LUKS-backed `vault.img` remained the effective security boundary.
3. `setup.enc` was recovered and decrypted locally, but it only bootstraps the install chain.
4. The real guarded runtime path depends on second-stage Phoenix artifacts: `phoenix.enc` and `phoenix_install.sh --guard`.
5. Those Phoenix artifacts were not recoverable locally during this engagement.
6. Internal-only recovery on the current box is therefore blocked in an evidence-backed way.

### Counterfactual paths worth mentioning carefully
- An unmodified original state may have supported cleaner testing of the intended unlock chain.
- Preserved original env values may have enabled a more direct validation of whether current or historical unlock logic matched the real vault key.
- Preserved local Phoenix artifacts may have enabled testing of the guarded runtime recovery chain.
- These belong only in a clearly labeled hypothesis section, not in the validated findings body.

### High-value evidence to reference
- **EVI-004 to EVI-007**: authorization gate, unlock path, service chain, and vault failure
- **EVI-008 to EVI-011**: shell-history recovery, repair-loop behavior, package/runtime inspection, and empty runtime placeholders
- **EVI-012**: decrypted `setup.enc` proving the Phoenix second-stage bootstrap chain
- **EVI-013**: absence of surviving local Phoenix artifacts and lack of evidence-backed original env rollback source

## Evidence Index

| Evidence ID | Description | Source Path |
|---|---|---|
| EVI-001 | Charter and authorization initialization | `00-charter/` |
| EVI-002 | Prior research artifacts and setup-script review | `research/ntv-hardware-lock/source/drive/` |
| EVI-003 | Operator live-target observations | `01-recon/recon-summary.md` |
| EVI-004 | Live auth logic and vault inspection outputs | operator attachments |
| EVI-005 | Current serial/CID/hash validation and direct unlock failure | operator attachments |
| EVI-006 | Service, symlink, timestamp, and journal outputs | operator attachments |
| EVI-007 | Repairman/watchdog and mount-path inspection outputs | operator attachments |
| EVI-008 | Forensic sweep part 1, shell history and path inventory | `incoming/forensic-sweep-2026-04-14-part1.md` |
| EVI-009 | Forensic sweep part 2, repair-loop traces | `incoming/forensic-sweep-2026-04-14-part2.md` |
| EVI-010 | Forensic sweep part 3, package traces and repair-root search logic | `incoming/forensic-sweep-2026-04-14-part3.md` |
| EVI-011 | Forensic sweep part 4, empty runtime directories and repairman logic | `incoming/forensic-sweep-2026-04-14-part4.md` |
| EVI-012 | Local `setup.enc` decryption and bootstrap analysis | operator outputs and `~/hardwarelockv2-artifacts/setup.dec.sh` |
| EVI-013 | Local searches showing no surviving Phoenix installer artifacts or original tuple rollback source | operator outputs and local note captures |

## Publishing Notes

- Final local deliverables were updated under `engagements/hardwarelockv2/06-report/`.
- No publication link was generated in this run because no external Google Docs/Slides publishing step was executed.
- If publishing is required later, use the finalized markdown deliverables as the source of truth.

## Cleanup / Restoration Reference

Tester-created artifacts introduced: none beyond engagement documentation  
Tester-created artifacts removed: none  
Tester-created artifacts remaining intentionally: report package and engagement notes  
Environment restored to agreed state: no additional live changes introduced by reporting  
Residual risk after cleanup: weak local auth, exposed provisioning traces, and fragile artifact-dependent recovery remain relevant  
Client follow-up required: yes, obtain trusted recovery artifacts before further recovery attempts
