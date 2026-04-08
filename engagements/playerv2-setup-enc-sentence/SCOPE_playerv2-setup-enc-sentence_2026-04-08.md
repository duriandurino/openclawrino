# Scope — playerv2-setup-enc-sentence

**Date:** 2026-04-08
**Target:** `engagements/playerv2-artifacts/inbound/setup.enc`
**Engagement Type:** Full local artifact pentest, sentence-passphrase lead
**Authorization Basis:** User explicitly requested a full pentest on the local `setup.enc` artifact and directed this run to begin with reconnaissance.

## In Scope

- Reconnaissance on `setup.enc` and adjacent local context
- Correlation with PlayerV2 / NTV installer and hardware-lock research already present in the workspace
- Passphrase-recovery hypothesis development from evidence, including the new operator clue that the passphrase is a sentence
- Safe staged progression into later enum, vuln, and exploit phases after recon

## Constraints

- Preserve the original encrypted artifact untouched
- Do not claim contents of `setup.enc` without successful decryption or equivalent verification
- Treat `pentest_engagement.zip` as intended recon input, but note that it was not present in the workspace at recon time
- Avoid blind brute-force claims; prefer evidence-backed passphrase generation and validation paths
