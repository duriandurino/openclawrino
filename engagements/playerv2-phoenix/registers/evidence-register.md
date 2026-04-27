# Evidence Register

| Evidence ID | Phase | Type | Source | Timestamp | Related finding | Sensitivity | Storage path | Sanitized? |
|---|---|---|---|---|---|---|---|---|
| E-001 | recon | screen photo / operator observation | physical device screen | 2026-04-27 15:01 GMT+8 | wrong-device lockout state, trust-control failure messaging | internal | operator-submitted photos, noted in `engagements/playerv2-phoenix/recon/recon-evidence-index.md` | partial |
| E-002 | recon | console observation | tty2 / tty3 / tty4 / tty5 / tty6 | 2026-04-27 15:43-18:55 GMT+8 | alternate TTY exposure, hostname/IP/banner disclosure, repeated login surfaces | internal | `engagements/playerv2-phoenix/recon/recon-evidence-index.md` | yes |
| E-003 | enum | TCP enumeration log | operator VM to `192.168.1.70` | 2026-04-27 18:27 GMT+8 | validated SSH and rpcbind TCP exposure | internal | `engagements/playerv2-phoenix/enum/live/network-enum-2026-04-27_1827.txt` | yes |
| E-004 | enum | RPC validation log | operator VM to `192.168.1.70` | 2026-04-27 18:29 GMT+8 | rpcbind exposure limited to portmapper registrations, no proven NFS export | internal | `engagements/playerv2-phoenix/enum/live/rpcinfo-2026-04-27_1829.txt` | yes |
| E-005 | enum | UDP enumeration log | operator VM to `192.168.1.70` | 2026-04-27 18:32 GMT+8 | validated `111/udp` and `5353/udp`; reduced UDP uncertainty | internal | `engagements/playerv2-phoenix/enum/live/udp-enum-2026-04-27_1832.txt` | yes |
| E-006 | enum | API enumeration log | operator VM to `dev-api.n-compass.online` | 2026-04-27 18:34 GMT+8 | AWS ELB front, Kestrel-backed 404 hints, thin public response surface | internal | `engagements/playerv2-phoenix/enum/live/api-linkage-2026-04-27_1834.txt` | yes |
| E-007 | enum | SSH deep fingerprint log | operator VM to `192.168.1.70` | 2026-04-27 18:34 GMT+8 | SSH auth methods and host-key evidence | internal | `engagements/playerv2-phoenix/enum/live/ssh-deep-2026-04-27_1834.txt` | yes |
| E-008 | enum | targeted UDP follow-up log | operator VM / LAN multicast responses | 2026-04-27 18:42 GMT+8 | reclassified `137/udp` and `1900/udp` as closed on the Pi; identified unrelated LAN SSDP noise | internal | `engagements/playerv2-phoenix/enum/live/udp-followup-2026-04-27_1842.txt` | yes |
| E-009 | enum | runtime constraint note | current Telegram direct runtime | 2026-04-27 18:41 GMT+8 | passive packet capture blocked due to lack of elevated access in this session | internal | `engagements/playerv2-phoenix/enum/enum-activity-log.md` | yes |
