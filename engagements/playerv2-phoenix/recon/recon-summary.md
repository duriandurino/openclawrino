# Recon Summary

## Reproducibility and Process Notes

This recon summary is meant to preserve both what was observed and how the observation happened.

For the physical portions of recon, reproducibility depends on repeating the same local interaction pattern on the target device, especially:
- observing the wrong-device or lockout state directly
- trying `Alt+F1` through `Alt+F6` to test whether alternate TTYs are exposed
- pressing `F1` during early startup to test whether the boot path can be diverted into the visible SD-mode text path
- recording exactly what appears on screen after each key sequence

For the network-supporting portions of recon, the later enum commands are the strongest replay guide once the local IP is revealed, especially after the TTY exposure shows `192.168.1.70`.

- Recon is authorized to begin under the current operator interpretation of the client's broad testing language for the named target and selected surfaces
- Current confirmed in-scope item from the pre-engagement record: `https://dev-api.n-compass.online`
- Current posture: low-risk, evidence-first reconnaissance while preserving caution around ambiguous or higher-impact activities
- Immediate recon objective: establish a trustworthy first-pass asset and attack-surface inventory for Player v2 - Phoenix
- New live operator observations expand the recon picture beyond the API surface and suggest a device-side authorization and secure-storage dependency path worth mapping before deeper testing
- Current working recon hypothesis: the target may use a hardware-bound authorization check that gates a vault or protected storage mount, and failure in that chain may explain the unauthorized-hardware state and wrong-device prompt observed locally
- Controlled TTY switching now confirms that the lockout screen does not fully isolate alternate virtual consoles after failure conditions appear, and that the device exposes login consoles with host and network details
- TTY switching method correction: this was not `Ctrl+Alt+Fn`. The operator confirmed the working console-switch path was `Alt+Fn`.
- That TTY exposure was not found by accident. The operator asked OpenClaw what keys to try next, then tested the suggested TTY-switching path. `Alt+F2` and `Alt+F3` worked first, later expanding to the same pattern across `tty2` through `tty6`, while `Alt+F1` returned to the wrong-device prompt on the main console
- Newly confirmed device details from local console observation:
  - visible text on exposed alternate consoles included:
    - `Debian GNU/Linux 13 raspberry tty2`
    - `Debian GNU/Linux 13 raspberry tty3`
    - `My IP address is 192.168.1.70`
    - `raspberry login:`
  - hostname: `raspberry`
  - OS banner: `Debian GNU/Linux 13`
  - IPv4 address: `192.168.1.70`
  - link-local IPv6 address observed: `fe80::2ecf:67ff:fe04:bd1`
- Additional operator observation to validate in follow-up testing:
  - shortcut correction history:
    - initial belief: `Ctrl+Alt+Esc`
    - later belief: `Alt+Esc`
    - latest operator correction: the shutdown-triggering shortcut is `Fn+Esc`
  - `Fn+Esc` appears to cause the player device to turn off or shut down
  - current confidence was initially low, but later photo evidence strongly suggests this path reaches a real systemd shutdown / poweroff sequence rather than only killing the player UI
  - visible shutdown-sequence evidence now includes:
    - `Reached target shutdown.target - System Shutdown.`
    - `Reached target poweroff.target - System Power Off.`
    - `Started plymouth-poweroff.service - Show Plymouth Power Off Screen.`
  - additional operator finding: near the verge of shutdown, pressing `Shift+Esc` appears to expose the stopped-services log output on screen
  - if reproduced consistently, this indicates an exposed local denial-of-service path with likely full device impact, not just a kiosk escape
- New boot-sequence recon from operator photos and live observation:
  - this path was explored after the operator asked for more keys to try during boot, specifically looking for interactions similar to the earlier `F1` behavior
  - during early startup, pressing `F1` can divert execution into an SD / boot-text path that visibly shows `Progress: Trying boot mode SD`
  - while the NTV logo / Plymouth screen is running, pressing `Esc` can reveal a short-lived startup log screen before `tty1` takes over
  - this revealed boot/service lines including local and remote filesystem setup, multiple socket units, `cloud-init` stages, `NetworkManager`, Raspberry Pi EEPROM update checks, and a visible line `Complete socket interaction for boot stage local`
  - the same early window can temporarily expose a GUI-like environment where the start menu and apps are reachable before the lockout path reasserts itself
  - the earlier `tty1` shell exposure has recently stopped appearing even though the operator reports no intentional change; current live behavior is now that only the OS GUI appears before the later takeover
  - current interpretation: there is a short boot-phase race or stage transition before the hardware-lock workflow fully takes control of the primary console, but the exact visible presentation of that race may be nondeterministic across boots
  - later startup and shutdown photo evidence adds a stronger service-order clue: `systemd[1]: graphical.target: Job nctv-phoenix.target/start deleted to break ordering cycle starting with graphical.target/start` alongside the previously observed Phoenix / hardware-check ordering-cycle clue
  - this suggests the Phoenix startup chain and the hardware-check path are linked by a systemd ordering-cycle condition, which may help explain why GUI or shell exposure can appear before the intended lockout path fully asserts, and why the `tty1` shell exposure is not consistently present on every boot
  - operator also relayed this exposure to the client for early defensive remediation; the current working theory is that `hardware-check.service` is starting after GUI / `tty1` exposure instead of before it, so the likely remediation path is service-order hardening
  - important engagement note: despite that early notice to the client, the current `playerv2-phoenix` version under test is expected to remain unchanged during this pentest, so findings and timing observations should continue to be treated as applying to the present build unless live evidence later shows otherwise
