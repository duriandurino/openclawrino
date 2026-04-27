# Recon Next Actions

- Recon evidence is now sufficient to hand off into enumeration for the current device and API surfaces
- Preserve the current recon conclusions as the phase handoff baseline:
  - confirmed API target `https://dev-api.n-compass.online`
  - local device hostname `raspberry`
  - local IPv4 `192.168.1.70`
  - local link-local IPv6 `fe80::2ecf:67ff:fe04:bd1`
  - visible login consoles on tty2 and tty3
  - observed trust-control components `hardware-check.service` and `vault-mount.service`
- Note the remaining recon uncertainty that may affect enum planning:
  - the operator VM is connected to Wi-Fi SSID `NTV360_5GHz`
  - the player Raspberry Pi Wi-Fi / SSID is still unknown
  - same-LAN reachability is not yet confirmed only from the shared IPv4 private range
- Defer deeper active probing to enum, especially SSH reachability checks, systemd/service inspection, and host-level validation
- Preserve the current physical recon conclusion for enum and later reporting:
  - tty2 through tty6 are exposed login surfaces in the failure state
  - tty1 remains the wrong-device prompt surface
  - default `pi` / `raspberry` login did not succeed
