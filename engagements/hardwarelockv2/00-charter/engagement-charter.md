# Engagement Charter

- **Engagement title:** Unlock Player with Hardware Lock V2
- **Target:** hardwareLockV2
- **Test type:** Gray Box, Application Image, Raspi
- **Start date:** 2026-04-13
- **End date:** 2026-04-13
- **Status:** authorized
- **Approval / authorization reference:** Authorized for pentest by Arjay Saguisa
- **Success criteria:** unlock os, display service files, run the service files
- **Primary analyst:** Hatless White
- **Supporting agents:** specter-recon, specter-enum, specter-vuln, specter-exploit, specter-post, specter-report

## Objectives

- TBD

## Constraints

- no passphrase info for image lock; no info about process or code file pattern; do not break whole system

## Credentials Provided

- none; sudo currently accessible; info about raspi serial and sd card serial being used as hardware lock

## Communications

- **Primary contact:** TBD
- **Escalation contact:** TBD
- **Stop condition contact:** TBD

## Notes

- Initialized by `scripts/orchestration/init_engagement_docs.py`
