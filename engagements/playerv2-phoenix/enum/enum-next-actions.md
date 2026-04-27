# Enum Next Actions

- Preserve the validated Phoenix Pi service inventory as the current enum baseline:
  - `22/tcp` SSH
  - `111/tcp` and `111/udp` rpcbind
  - `5353/udp` mDNS / Zeroconf
- Treat `137/udp`, `1900/udp`, and `123/udp` as resolved non-findings for the current host unless fresh contradictory evidence appears
- Keep the Pi/API relationship labeled as likely but unproven until a stronger shared identifier, outbound flow, config artifact, or on-device evidence ties them directly together
- If privileged local capture becomes available later, use it to correlate mDNS advertisements and outbound `n-compass.online` traffic from `192.168.1.70`
- Prioritize physical or on-device enum next, because the strongest remaining evidence path is no longer blind network expansion:
  - tty2 through tty6 remain exposed login surfaces
  - tty1 remains the wrong-device prompt
  - observed trust-control components are still `hardware-check.service` and `vault-mount.service`
- Avoid broad credential guessing; only test small, evidence-backed hypotheses if new on-device clues justify them
- Preserve reporting-ready reality-check language:
  - sparse but real network surface confirmed
  - alternate local consoles exposed in the failure state
  - no validated console access yet
  - no proven direct API trust binding yet
