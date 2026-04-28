# Recon Summary

## Reproducibility and Process Notes

This recon summary is meant to preserve both what was observed and how the observation happened.

For the physical portions of recon, reproducibility depends on repeating the same local interaction pattern on the target device, especially:
- observing the wrong-device or lockout state directly
- trying `Ctrl+Alt+F1` through `Ctrl+Alt+F6` to test whether alternate TTYs are exposed
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
- That TTY exposure was not found by accident. The operator asked OpenClaw what keys to try next, then tested the suggested TTY-switching path. `Ctrl+Alt+F2` and `Ctrl+Alt+F3` worked first, later expanding to the same pattern across `tty2` through `tty6`, while `Ctrl+Alt+F1` returned to the wrong-device prompt on the main console
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
  - `Ctrl+Alt+Esc` appears to cause the player device to turn off or shut down
  - current confidence: low until reproduced and distinguished between full shutdown, player-process exit, display blanking, or watchdog-triggered restart
  - if reproduced consistently, this may indicate an exposed local denial-of-service or kiosk-escape-adjacent control path worth carrying into enum/vuln validation
- New boot-sequence recon from operator photos and live observation:
  - this path was explored after the operator asked for more keys to try during boot, specifically looking for interactions similar to the earlier `F1` behavior
  - during early startup, pressing `F1` can divert execution into an SD / boot-text path that visibly shows `Progress: Trying boot mode SD`
  - the same early window can temporarily expose a GUI-like environment where the start menu and apps are reachable before the lockout path reasserts itself
  - this GUI exposure appears transient and is overtaken later by the unauthorized-device / wrong-device path on `tty1`
  - current interpretation: there is a short boot-phase race or stage transition before the hardware-lock workflow fully takes control of the primary console
  - operator also relayed this exposure to the client for early defensive remediation; the current working theory is that `hardware-check.service` is starting after GUI / `tty1` exposure instead of before it, so the likely remediation path is service-order hardening
  - important engagement note: despite that early notice to the client, the current `playerv2-phoenix` version under test is expected to remain unchanged during this pentest, so findings and timing observations should continue to be treated as applying to the present build unless live evidence later shows otherwise
