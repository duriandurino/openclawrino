# Enum Activity Log

- 2026-04-27 15:52 GMT+8 — Enum phase opened based on completed recon covering the confirmed API target, local device hostname/IP exposure, alternate tty login consoles, and observed trust-control service names
- 2026-04-27 15:52 GMT+8 — Recorded starting enum uncertainty that the operator VM is on Wi-Fi SSID `NTV360_5GHz` while the player Raspberry Pi Wi-Fi / SSID remains unknown, so same-segment reachability must be validated before remote assumptions are made
- 2026-04-27 16:01 GMT+8 — Validated that the player is reachable from the operator VM: ICMP succeeded to `192.168.1.70`, TCP/22 was open, and SSH accepted connections up to authentication
- 2026-04-27 16:41 GMT+8 — Fingerprinted SSH on the player as `OpenSSH 10.0p2 Debian 7+deb13u2` and collected host keys and algorithm support with low-noise SSH enumeration
- 2026-04-27 16:41 GMT+8 — Performed parallel low-noise API enumeration against `dev-api.n-compass.online`, confirming AWS load-balancer hosting, simple `This is N-Compass TV.` body content, public AWS IP resolution, and TLS certificate subject `n-compass.online`
- 2026-04-27 18:05 GMT+8 — Finalized Ena's first network enum finding set into the engagement notes: reachable Pi over SSH, validated OpenSSH fingerprint, and externally reachable API surface behind AWS ELB
- 2026-04-27 18:27 GMT+8 — Expanded TCP enumeration on `192.168.1.70`, confirming only `22/tcp` and `111/tcp` open in the full sweep and identifying `111/tcp` as `rpcbind 2-4`
- 2026-04-27 18:29 GMT+8 — Validated the exposed RPC surface with `rpcinfo`, `showmount`, and Nmap RPC scripting; confirmed only portmapper registrations and no proven NFS exports or higher RPC programs
- 2026-04-27 18:32 GMT+8 — Completed UDP enumeration, confirming `111/udp` (`rpcbind`) and `5353/udp` (`mDNS / Zeroconf`) while reclassifying `123/udp` as closed after targeted follow-up
- 2026-04-27 18:34 GMT+8 — Deepened API-side enumeration and observed that `/api`, `/api/health`, and `/api/v1` return `404` with `Server: Kestrel`, indicating an application tier behind the AWS ELB despite the thin public response surface
- 2026-04-27 18:34 GMT+8 — Deepened SSH enumeration, confirming host keys for RSA, ECDSA, and ED25519 plus accepted auth methods `publickey,password`
- 2026-04-27 18:41 GMT+8 — Attempted passive local-network correlation for Pi / API traffic, but elevated packet capture was blocked from the current Telegram runtime
- 2026-04-27 18:42 GMT+8 — Performed targeted follow-up on UDP candidates `137/udp` and `1900/udp`; both reclassified as closed on the Pi, while observed SSDP responses were attributed to other LAN devices rather than the target
- 2026-04-27 18:55 GMT+8 — Coordinated physical-enum follow-up with the operator and confirmed the TTY exposure pattern remained stable: tty2 through tty6 show matching login consoles, tty1 remains the wrong-device prompt, and default `pi` / `raspberry` access still fails
