# Master Activity Log

- Initialize entries here as work begins

## 2026-04-13 11:55 PST - Engagement initialized

- **Phase:** pre-engagement
- **Objective:** capture intake and authorize documentation-first kickoff
- **Target:** hardwareLockV2
- **Action performed:** initialized engagement structure and recorded charter/ROE from user-supplied intake
- **Tool / command:** python3 scripts/orchestration/init_engagement_docs.py hardwarelockv2 ...
- **Result:** engagement folder, charter, scope/ROE, phase docs, and central registers created
- **Evidence ID:** EVI-001
- **Analyst notes:** authorization reference provided by user; active testing allowed within non-destructive constraints
- **Next step:** start recon focused on app image, lock mechanism clues, and service file locations

## 2026-04-13 11:56 PST - Reviewed existing hardware lock documentation and setup scripts

- **Phase:** recon
- **Objective:** identify known lock mechanics, image handling, and service startup paths before touching live artifacts
- **Target:** hardwareLockV2
- **Action performed:** searched workspace for hardware-lock, player, image, and service artifacts; reviewed research notes and setup script copies
- **Tool / command:** find ... ; read research/ntv-hardware-lock/... documentation and setup script
- **Result:** recovered concrete lock design, authorized serial values, service chain, vault unlock path, and watchdog behavior from prior artifacts
- **Evidence ID:** EVI-002
- **Analyst notes:** strongest lead is serial-bound hardware_lock.py plus serial-derived vault unlock path; watchdog and repairman introduce destructive-risk edges if app dir or boot config is altered
- **Next step:** extract validated hypotheses and log candidate bypass paths without modifying the target yet

## 2026-04-13 14:23 PST - Logged operator-supplied live-target progress

- **Phase:** recon
- **Objective:** capture current live-target observations and already-taken actions before further guidance
- **Target:** hardwareLockV2
- **Action performed:** recorded user-reported TTY lock behavior, filesystem discoveries, and manual environment file edit already performed on target
- **Tool / command:** user report
- **Result:** gained current-state visibility into live target paths and one prior modification to `/etc/nctv-phoenix/hardware-lock.env`
- **Evidence ID:** EVI-003
- **Analyst notes:** target state is no longer pristine because authorized hardware values were already changed in the env file; subsequent validation should account for that and avoid additional destabilizing edits
- **Next step:** update recon findings and choose the safest next enumeration/validation step around the modified live state

## 2026-04-13 15:13 PST - Analyzed live Hardware Lock V2 logic and vault state

- **Phase:** enum
- **Objective:** confirm V2 authorization checks, unlock key derivation, and current vault mount state
- **Target:** hardwareLockV2
- **Action performed:** reviewed user-supplied contents of `hardware_lock.py`, `unlock_vault.py`, `hardware-lock.env`, and vault metadata outputs
- **Tool / command:** operator-supplied `cat`, `file`, `cryptsetup luksDump`, `mount`, and `ls /dev/mapper` outputs
- **Result:** confirmed env-based authorization, deterministic unlock key derivation, LUKS2 vault presence, and that no mapper or vault mount is currently active
- **Evidence ID:** EVI-004
- **Analyst notes:** edited env now matches current device, so remaining blocker is likely the derived key not opening the vault or secure runtime paths missing inside the mounted image
- **Next step:** validate current serial/CID values against env and test unlock path directly while preserving logs

## 2026-04-13 17:06 PST - Brought enum status to current state after live validation and recovery-path review

- **Phase:** enum
- **Objective:** reconcile current live unlock failure, service dependencies, and recovery-path availability
- **Target:** hardwareLockV2
- **Action performed:** analyzed live serial/CID match, direct `unlock_vault.py` failure, service unit chain, broken player symlink, journal restart loop, and recovery/watchdog scripts
- **Tool / command:** operator-supplied outputs from live target commands and service logs
- **Result:** confirmed current authorization values match hardware, current unlock derivation does not unlock the real LUKS vault, player runtime path remains absent until vault content is exposed, and no external repair payload is mounted
- **Evidence ID:** EVI-005, EVI-006, EVI-007
- **Analyst notes:** current live scripts are modified state, especially `unlock_vault.py`; the engagement is blocked on recovering original vault key material or provisioning payload rather than additional launcher/service tweaking
- **Next step:** preserve blocked-state documentation, avoid further blind edits, and pivot to recovery of original provisioning artifacts or last-chance forensic sweep if desired

## 2026-04-14 11:xx PST - Planned targeted forensic sweep for recovery remnants

- **Phase:** exploit
- **Objective:** define the safest next collection sequence for recovering historical keying or provisioning artifacts without destabilizing the target
- **Target:** hardwareLockV2
- **Action performed:** reviewed charter, ROE, recon/enum/vuln handoff notes, and exploit blockers to design a read-first forensic sweep
- **Tool / command:** document review and engagement planning
- **Result:** selected a low-risk search order focused on history, logs, package traces, service/tmp paths, removable-media records, and only then optional deleted-file residue checks
- **Evidence ID:** EVI-001, EVI-004, EVI-005, EVI-006, EVI-007
- **Analyst notes:** sweep should avoid service edits, watchdog-triggering file moves, and repeated live unlock loops
- **Next step:** run the forensic sweep checklist on-box and capture any provisioning or recovery remnants as new evidence

## 2026-04-14 12:08 PST - Triage of forensic sweep produced new provisioning and repair-path leads

- **Phase:** exploit
- **Objective:** determine whether the read-first forensic sweep exposed original provisioning clues or external recovery dependencies
- **Target:** hardwareLockV2
- **Action performed:** analyzed operator-provided sweep outputs covering shell history, journals, dpkg traces, temp paths, and repairman search logic
- **Tool / command:** review of Telegram-delivered command output artifacts
- **Result:** recovered a historical provisioning command that fetched `setup.enc`, decrypted it with passphrase `theNTVofthe360isthe360oftheNTV`, and piped it to `sudo bash`; also confirmed the repair workflow expects an external `nctv-phoenix` source and identified `/var/tmp/dispsetup.sh` plus packaged `app.asar` as next artifacts to inspect
- **Evidence ID:** EVI-008, EVI-009, EVI-010
- **Analyst notes:** this is the strongest lead so far because it points to original installer logic instead of guessing vault derivation from current modified scripts
- **Next step:** inspect `/var/tmp/dispsetup.sh`, package metadata, and player resources, and, if available, reacquire or test-decrypt the historical `setup.enc` artifact with the recovered passphrase

## 2026-04-14 13:17 PST - Narrow artifact inspection ruled out obvious local installer leftovers

- **Phase:** exploit
- **Objective:** test whether leftover setup or package artifacts on-box contain provisioning or unlock logic
- **Target:** hardwareLockV2
- **Action performed:** reviewed `/var/tmp/dispsetup.sh`, `dpkg -s nctv-player`, `nctv-player.postinst`, and performed shallow strings/grep inspection across `app.asar` and unpacked runtime paths
- **Tool / command:** operator-run read-only artifact inspection commands
- **Result:** `dispsetup.sh` is display-only, package metadata is routine, postinst only manages symlink/SUID setup, and the shallow resource scan did not reveal obvious provisioning or unlock logic
- **Evidence ID:** EVI-010
- **Analyst notes:** the best remaining live leads are now the historical `setup.enc` path and a deeper `app.asar` extraction if we need to inspect app internals beyond surface strings
- **Next step:** either reacquire/test `setup.enc` with the historical passphrase or extract `app.asar` for deeper application review

## 2026-04-14 13:29 PST - Confirmed empty runtime placeholders and explicit external-repair dependency

- **Phase:** exploit
- **Objective:** verify whether meaningful runtime payload remains locally and whether repairman can proceed without external artifacts
- **Target:** hardwareLockV2
- **Action performed:** inspected current runtime directories, reviewed `repairman.sh` directly, and searched local paths for candidate repair trees and installer artifacts
- **Tool / command:** operator-run read-only filesystem and script inspection commands
- **Result:** `/opt/nctv-player`, `/var/lib/nctv-player`, and `/mnt/nctv-phoenix-secure` are effectively empty placeholders; `repairman.sh` explicitly requires an external `nctv-phoenix` tree and refuses plaintext local restore when the vault is locked; no valid external/local repair source was found in this pass
- **Evidence ID:** EVI-011
- **Analyst notes:** this strongly suggests the current device is locally exhausted as a recovery source and that the next meaningful progress requires external artifacts, sibling-device comparison, or the historical installer path
- **Next step:** pivot from local squeezing to acquiring the missing repair source or recovering the historical `setup.enc` installer flow

## 2026-04-14 13:55 PST - Preserved post-sweep interpretation of player-versus-phoenix runtime state

- **Phase:** exploit
- **Objective:** capture the latest analytical conclusion before session drift and ensure the recovery model reflects new operator context
- **Target:** hardwareLockV2
- **Action performed:** reconciled the blocked unlock state with the new operator insight that the player runtime and phoenix payload are expected to exist together rather than as independent recoveries
- **Tool / command:** analyst interpretation from current engagement evidence plus operator clarification
- **Result:** documented that env edits only satisfy the authorization gate for OS-level progression; they do not restore the actual player because the expected phoenix-plus-player runtime bundle is still locked, absent, or expected from external recovery media or historical installer flow
- **Evidence ID:** EVI-011
- **Analyst notes:** this reinforces that the problem is now runtime provenance and payload recovery, not just passphrase alignment; if phoenix is absent, player cannot appear even when authorization passes
- **Next step:** treat `vault.img`, historical `setup.enc`, external repair media, and sibling-device comparison as the primary recovery hypotheses for the combined phoenix-plus-player bundle

## 2026-04-14 14:33 PST - Decrypted local setup.enc and identified Phoenix bootstrap chain

- **Phase:** exploit
- **Objective:** determine whether the locally recovered `setup.enc` artifact can explain the missing runtime and vault behavior without fetching new external artifacts
- **Target:** hardwareLockV2
- **Action performed:** decrypted local `~/Downloads/setup.enc` with the shell-history passphrase, reviewed the bootstrap script, and extracted the player and Phoenix installation flow
- **Tool / command:** operator-run `openssl enc -aes-256-cbc -d -salt -pbkdf2 ...`, `file`, `head`, `grep`, and `sed` against `setup.dec.sh`
- **Result:** confirmed `setup.enc` is a bootstrap installer that creates player directories, registers the device, installs `nctv-player` from `http://3.211.184.159:8080`, then downloads `phoenix.enc`, decrypts it with the same passphrase, extracts `nctv-phoenix`, and runs `./phoenix_install.sh --guard`
- **Evidence ID:** EVI-012
- **Analyst notes:** the real guarded runtime logic likely lives in `phoenix.enc` and `phoenix_install.sh`, not directly in `setup.enc`; this sharply narrows the missing artifact chain
- **Next step:** verify whether any local copy of `phoenix.enc`, extracted `nctv-phoenix`, or `phoenix_install.sh` remains on-box, and update the blocked-state conclusion if none exists

## 2026-04-14 14:43 PST - Confirmed Phoenix installer artifacts are absent locally and bounded the internal-only recovery lane

- **Phase:** exploit
- **Objective:** test whether the newly identified Phoenix artifact chain can still be recovered from local storage only
- **Target:** hardwareLockV2
- **Action performed:** searched local user, temp, runtime, and library paths for `phoenix.enc`, Phoenix tarballs, `phoenix_install.sh`, and extracted `nctv-phoenix` remnants; cross-checked env-history traces and document snapshots for recoverable original tuple values
- **Tool / command:** operator-run `find`, `grep`, and read-only note/history review
- **Result:** no local `phoenix.enc`, `phoenix_install.sh`, or extracted `nctv-phoenix` tree was found; only `/var/lib/nctv-phoenix/vault.img` remains. History and note captures preserve only the already-edited current env values, not the original authorized tuple
- **Evidence ID:** EVI-013
- **Analyst notes:** this makes the current box effectively end-of-line for internal-only runtime recovery. The env edit did not by itself create the blocker; rather, it exposed that the surviving local artifacts are insufficient to reconstruct the original Phoenix provisioning context or original authorized tuple
- **Next step:** preserve the engagement as an evidence-backed blocked state. Further progress requires a legitimate recovery source such as original provisioning material, original tuple provenance, or other authorized artifact chain outside the current local residue set
