# Attack Path Register

| Attack Path ID | Status | Summary | Prerequisites | Evidence | Notes |
|---|---|---|---|---|---|
| AP-001 | validated-non-terminal | Edit `hardware-lock.env` to align the local authorization gate with current hardware | local file edit access on target | EVI-004, EVI-005 | Authorization passes, but vault remains locked |
| AP-002 | candidate-blocked | Recover original provisioning logic or historical key material to reconstruct the real vault unlock path | installer/remnant access, sibling device, or forensic recovery source | EVI-004, EVI-006, EVI-007 | Most plausible next path |
| AP-003 | candidate-blocked | Locate and inspect the external repair payload expected by `repairman.sh` | repair media, mounted source, or archived bundle | EVI-006, EVI-007 | Could expose runtime files or unlock helpers indirectly |
| AP-004 | optional-last-resort | Attempt offline recovery against `vault.img` using targeted derivation hypotheses | explicit authorization, lab workflow, time budget | EVI-004, EVI-005 | Likely low-yield without stronger key hypotheses |
| AP-005 | candidate-high-value | Recover or reproduce the historical `setup.enc` provisioning flow using the passphrase found in shell history | access to `setup.enc` or preserved installer artifacts | EVI-008 | Strongest new lead because it may reveal original provisioning logic or key material |
| AP-006 | candidate-low-yield | Inspect leftover installer/runtime artifacts such as `/var/tmp/dispsetup.sh`, `/opt/nctv-player/resources/app.asar`, and local notes for references to repair/provisioning logic | read access to leftover scripts and packaged app files | EVI-008, EVI-010, EVI-011 | Local leftovers were mostly ruled out; current target retains placeholder dirs more than real payload |
| AP-007 | validated-blocked | Use local repairman workflow to restore the runtime from an external `nctv-phoenix` tree | access to valid external repair source | EVI-009, EVI-010, EVI-011 | The code path exists and is explicit, but cannot proceed without the missing external tree |
