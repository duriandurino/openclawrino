# Recon Findings Delta

- confirmed leads:
  - serial and SD-CID hardware binding exists in prior implementation artifacts
  - vault/image unlock path likely uses Pi serial-derived key material
  - service startup likely comes from `/home/pi/n-compasstv-secure/ecosystem.config.js`
- suspected leads:
  - Hardware Lock V2 may reuse these mechanics with changed constants or slightly altered unlock flow
  - `setup.enc` or related player-vault artifacts may contain V2-specific clues
- unresolved items:
  - actual V2 file locations on target
  - actual V2 authorized serial/CID values
  - actual V2 service file layout and runtime dependencies
- escalation to next phase is justified: yes, into focused enumeration of V2 artifacts and lock logic
