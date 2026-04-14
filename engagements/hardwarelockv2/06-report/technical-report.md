# Technical Report

## Final Exploit Conclusion

The Hardware Lock V2 assessment reached a verified blocked state rather than a full runtime recovery. Testing confirmed that the local authorization gate can be influenced by editing `hardware-lock.env`, allowing the current hardware tuple to satisfy the initial device check. However, this did not translate into payload access because the independent LUKS-protected `vault.img` remained the effective security boundary.

Direct execution of `unlock_vault.py` continued to fail with `cryptsetup` key rejection, demonstrating that matching the current device against the edited environment file is not sufficient to unlock the secure runtime. Subsequent analysis showed that the expected player runtime and Phoenix payload operate as a coupled chain, and that the local `setup.enc` artifact is only a bootstrap installer. It installs `nctv-player`, then retrieves and decrypts a second-stage `phoenix.enc` package and runs `phoenix_install.sh --guard`.

At the time of validation, no local copy of `phoenix.enc`, no extracted `nctv-phoenix` tree, and no recoverable original authorized tuple were present on the target. The device retained only `vault.img` plus placeholder runtime directories, while repair logic explicitly expected a missing external `nctv-phoenix` source. As a result, the engagement produced an evidence-backed conclusion: configuration integrity is weak enough to allow local authorization-gate manipulation, but the cryptographic vault and missing Phoenix provenance prevented full player/runtime restoration from the surviving on-box artifacts alone.

## Reporting Notes

- Report this engagement as a blocked but meaningful result, not as an incomplete write-up.
- Emphasize that the effective security control was the vault-bound runtime, while the weaker control was the editable local authorization configuration.
- Clearly separate validated findings from unverified next-step hypotheses.
