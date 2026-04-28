# Engagement Charter

- **Engagement title:** Player v2 - Phoenix
- **Target:** playerv2-phoenix
- **Test type:** Web application, API, and device / hardware / IoT
- **Start date:** 2026-04-24
- **End date:** 2026-05-01
- **Status:** sufficient for recon
- **Approval / authorization reference:** No explicit reference value entered. The field still contains template example text only.
- **Success criteria:**
  - Know the weak points and entry points of possible threat actors attacking the application
  - Find or confirm security gaps and RBAC exploits
  - Protect: Endpoint and Physical Access, Cloning of Image
- **Primary analyst:** Adrian C. Alejandrino
- **Supporting agents:** Hatless White, specter-recon, specter-enum, specter-vuln, specter-exploit, specter-post, specter-report

## Objectives

- Know the weak points and entry points of possible threat actors attacking the application
- Find or confirm security gaps and RBAC exploits
- Keep focus on endpoint and physical access plus cloning-of-image concerns named in the form

## Constraints

- The form includes a broad checked allowance through `Other: Test anything you want`, so unchecked items are not treated here as automatic denials by default
- The source also contains the literal free-text entry `Test all you want` under `Please list anything that must NOT be tested:`; it is preserved as-is because it is ambiguous
- Test accounts or credentials are not individually marked as provided in the form
- Operational contacts such as escalation and stop-condition contacts remain unspecified in the form

## Credentials Provided

- None explicitly provided in the form

## Communications

- **Primary contact:** Arjay Saguisa, Software Engineer, arjays@n-compass.online, +639222154772
- **Escalation contact:** not specified in the form
- **Stop condition contact:** not specified in the form

## Notes

- Process chain for this engagement:
  - the engagement was initiated from the user side through the `/pentest` workflow for the target
  - the Assigned Penetration Tester fill-up block was part of the intake path before the client form became the active source of engagement truth
  - the pre-engagement client form was spawned as a Google Doc
  - the client filled up that form
  - the completed form was then ingested into the local engagement docs and used as the source for charter and ROE interpretation
- Refreshed directly from the filled Google Doc pre-engagement form at `https://docs.google.com/document/d/1Msa0CrGZSOuyIciPtaeG6pkgWeo4ivYDQ7-5YC8vST4/edit`
- Assigned penetration tester block in the form names `Adrian C. Alejandrino` with email `adrian.alejandrino.1115@gmail.com`
- Ingestion method: `scripts/orchestration/ingest_pre_engagement_form.py` via `gog docs export --format md`
- Source workflow components relevant to this phase:
  - intake trigger: `/pentest <target>` workflow
  - form spawn path: pre-engagement form spawning workflow under `scripts/orchestration/`
  - ingest path: `scripts/orchestration/ingest_pre_engagement_form.py`
- Markdown export preserved checkbox/radio state; blank fields and template example text were left as-is instead of being treated as answered values
- Operator interpretation for this engagement: the client's `Test anything you want` language is treated as intended broad testing permission for the listed target and surfaces
- Current execution decision: pre-engagement is considered sufficient to begin reconnaissance and other low-risk validation work, but not yet polished enough to be treated as a fully finalized ROE package
- Higher-impact or ambiguous activities should still be handled conservatively until physical-testing language, stop conditions, and escalation contacts are clarified
- Interpretation policy matches `scope-and-roe.md`: the checked `Other: Test anything you want` entry is treated as materially broadening the apparent authorization, so unchecked items are not auto-converted into hard denials unless the source explicitly says so
- Initialized by `scripts/orchestration/init_engagement_docs.py`
