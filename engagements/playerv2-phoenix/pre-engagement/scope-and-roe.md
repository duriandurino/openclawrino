# Scope and Rules of Engagement

## Scope In

- Player v2 - Phoenix
- `https://dev-api.n-compass.online`
- Web application and device / hardware / IoT assessment surfaces that belong to the engagement target, subject to the constraints below

## Scope Out

- Denial of service or stress testing unless separately approved
- Social engineering unless separately approved
- Phishing unless separately approved
- Physical testing unless separately approved
- Third-party systems not explicitly listed in scope
- Accessing live customer content unless necessary
- Any action that changes or deletes production data
- Any AWS or other provider-managed assets that require separate provider approval, unless that approval is explicitly confirmed

## Rules of Engagement

- **Testing window:** 2026-04-24 through 2026-05-01, timezone GMT+8, exact daily window not yet specified
- **Allowed techniques:** Security testing of listed in-scope targets, safe confirmation of real weaknesses, use of provided test accounts if later supplied, limited proof-of-access demonstration where needed
- **Prohibited techniques:** DoS/stress testing, social engineering, phishing, physical testing, unapproved testing of third-party systems, unnecessary access to live customer content, any action that changes or deletes production data
- **DoS allowed?:** no
- **Persistence allowed?:** not approved
- **Social engineering allowed?:** no
- **Third-party / cloud approvals:** AWS is explicitly listed as the provider in the ingested form, but provider approval selection state is still not exposed by the current Google Docs structure output, so approval status remains unknown in the local record

## Safety Controls

- **Blackout periods:** none specified yet
- **Fragile systems / constraints:** protect uptime-sensitive endpoints and avoid disruptive testing; endpoint, physical access, and image cloning concerns were highlighted as important assets/risks
- **Emergency stop conditions:** any unexpected instability, service issues, or operator request to stop
- **Resume authority:** TBD

## Data Handling

- **Collection limits:** collect only what is necessary to validate weaknesses and report impact
- **Storage expectations:** workspace engagement folders only
- **Retention / destruction:** TBD
- **Sensitive data handling:** redact secrets from shared reporting

## Approval Status

- **Authorization confirmed?:** partially, the form includes approver identity and signature details plus an approval date, but checkbox selection state for explicit approval confirmation is not exposed by the current ingestion method
- **Provider approvals confirmed?:** unknown, AWS is named but the yes/no/not sure selection for provider permission is not exposed by the current ingestion method
- **Cleared for active testing?:** no, pending clarification of explicit approval selections, provider approval status, resume authority / stop contacts, and normalization of ambiguous scope language

## Notes

- Refreshed from the structured ingester output for the filled Google Doc pre-engagement form at `https://docs.google.com/document/d/1Msa0CrGZSOuyIciPtaeG6pkgWeo4ivYDQ7-5YC8vST4/edit`
- Ingestion method: `scripts/orchestration/ingest_pre_engagement_form.py` via `gog docs structure`
- The extracted form contains one ambiguous out-of-scope line, `Test all you want`, which conflicts with the rest of the ROE and should not be treated as authoritative without clarification
- Checkbox/radio selections remain unknown unless explicitly exposed by the Google Docs structure output, so unresolved selections are preserved as unknown rather than guessed
- Initialized by `scripts/orchestration/init_engagement_docs.py`
