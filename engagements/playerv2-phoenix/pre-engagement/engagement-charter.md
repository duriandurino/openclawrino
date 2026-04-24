# Engagement Charter

- **Engagement title:** Player v2 - Phoenix
- **Target:** playerv2-phoenix
- **Test type:** Web application and device / hardware / IoT assessment
- **Start date:** 2026-04-24
- **End date:** 2026-05-01
- **Status:** intake
- **Approval / authorization reference:** Approval confirmed in pre-engagement Google Doc signed by Arjay Saguisa on 2026-04-24, specific reference ID not provided
- **Success criteria:** Identify weak points, possible entry points, security gaps, and RBAC exploit opportunities affecting Player v2 - Phoenix
- **Primary analyst:** Hatless White
- **Supporting agents:** specter-recon, specter-enum, specter-vuln, specter-exploit, specter-post, specter-report

## Objectives

- Identify weak points and entry points a threat actor could use to attack the application
- Validate security gaps and RBAC exploit opportunities
- Assess risks related to endpoint exposure, physical access concerns, and image cloning concerns where allowed by the final ROE

## Constraints

- Do not perform denial of service or stress testing unless separately approved
- Do not perform social engineering or phishing unless separately approved
- Do not test third-party systems unless explicitly listed in scope and approved
- Do not access live customer content unless necessary
- Do not change or delete production data
- Physical testing appears disallowed unless separately approved, despite the broader stated desire to test aggressively; treat physical testing as not approved for now
- One extracted out-of-scope line from the source form is ambiguous and should be treated as needing clarification before active testing

## Credentials Provided

- None listed yet

## Communications

- **Primary contact:** Arjay Saguisa, Software Engineer, arjays@n-compass.online, +639222154772
- **Escalation contact:** TBD
- **Stop condition contact:** TBD

## Notes

- Populated from the filled Google Doc pre-engagement form at `https://docs.google.com/document/d/1Msa0CrGZSOuyIciPtaeG6pkgWeo4ivYDQ7-5YC8vST4/edit`
- Initialized by `scripts/orchestration/init_engagement_docs.py`
