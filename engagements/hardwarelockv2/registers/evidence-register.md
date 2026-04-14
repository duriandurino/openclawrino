# Evidence Register

| Evidence ID | Phase | Type | Source | Timestamp | Related finding | Sensitivity | Storage path | Sanitized? |
|---|---|---|---|---|---|---|---|---|
| EVI-001 | pre-engagement | note | user intake + init_engagement_docs.py | 2026-04-13 11:55 PST | N/A | internal | engagements/hardwarelockv2/00-charter/ | yes |
| EVI-002 | recon | note | workspace research docs and setup script copies | 2026-04-13 11:56 PST | N/A | internal | research/ntv-hardware-lock/source/drive/ | yes |
| EVI-003 | recon | note | operator live-target observations | 2026-04-13 14:23 PST | N/A | internal | engagements/hardwarelockv2/01-recon/recon-summary.md | yes |
| EVI-004 | enum | terminal output | live target file and vault inspection outputs | 2026-04-13 15:13 PST | N/A | internal | operator-provided markdown attachments 1.md, 2.md, 3.md | yes |
| EVI-005 | enum | terminal output | operator supplied current serial/CID/hash plus direct unlock failure | 2026-04-13 17:06 PST | N/A | internal | operator-provided markdown attachments | yes |
| EVI-006 | enum | terminal output | service, symlink, timestamp, and journal outputs | 2026-04-13 17:06 PST | N/A | internal | operator-provided markdown attachments | yes |
| EVI-007 | enum | terminal output | repairman/watchdog and mount-path inspection outputs | 2026-04-13 17:06 PST | N/A | internal | operator-provided markdown attachments | yes |
| EVI-008 | exploit | terminal output | forensic sweep, part 1, mounts, path inventory, shell history, local notes | 2026-04-14 12:08 PST | F-004 | internal | engagements/hardwarelockv2/incoming/forensic-sweep-2026-04-14-part1.md | yes |
| EVI-009 | exploit | terminal output | forensic sweep, part 2, systemd and journal repair-loop traces | 2026-04-14 12:08 PST | F-005 | internal | engagements/hardwarelockv2/incoming/forensic-sweep-2026-04-14-part2.md | yes |
| EVI-010 | exploit | terminal output | forensic sweep, part 3, dpkg/install traces, temp paths, repair-root search logic | 2026-04-14 12:08 PST | F-004, F-005 | internal | engagements/hardwarelockv2/incoming/forensic-sweep-2026-04-14-part3.md | yes |
| EVI-011 | exploit | terminal output | forensic sweep, part 4, empty runtime directories and direct repairman logic inspection | 2026-04-14 13:29 PST | F-005, F-006 | internal | engagements/hardwarelockv2/incoming/forensic-sweep-2026-04-14-part4.md | yes |
