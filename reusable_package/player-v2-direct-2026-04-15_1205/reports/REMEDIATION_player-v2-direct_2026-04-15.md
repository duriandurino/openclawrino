# Remediation Plan

## Immediate containment / hygiene
- Preserve a fresh live baseline before making any service or artifact changes.
- Hash and inventory any encrypted, installer, vault, or recovery-related artifacts before testing.
- Keep direct-assessment notes, screenshots, and command transcripts centralized under this package.

## Finding-specific remediation

### Encrypted installer workflow remains opaque without legitimate decryption knowledge
- **Problem:** Encrypted installer trust depends on unavailable or undocumented decryption knowledge.
- **Fix now:** document the authoritative decrypt-and-review workflow and identify legitimate key custodians.
- **Harden next:** ship signed manifests, expected hashes, and release metadata alongside encrypted packages.
- **Verify:** confirm a separate authorized operator can inspect the installer contents without tribal knowledge.

### Local-first trust boundaries should be reviewed before assuming network risk dominates
- **Problem:** Minimal remote exposure can hide the fact that local service startup, secrets, or recovery workflows carry the real risk.
- **Fix now:** review service unit files, startup wrappers, environment files, and operator history on the device.
- **Harden next:** reduce privileged startup paths, remove plaintext secrets, and tighten file permissions around app and repair scripts.
- **Verify:** confirm a fresh local enumeration pass finds no unnecessary secrets, writable launch paths, or undocumented privileged helpers.

## Architecture / process improvements
- Move encrypted deployment trust away from person-dependent knowledge.
- Preserve verifiable provenance for installer and repair artifacts.
- Document Phoenix or equivalent second-stage recovery dependencies so incident response is not blocked by missing external context.
- Maintain repeatable local assessment runbooks for field validation and retest.
