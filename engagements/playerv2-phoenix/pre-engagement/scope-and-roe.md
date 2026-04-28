# Scope and Rules of Engagement

## Scope In

- System / application / project name(s): Player v2 - Phoenix
- Included testing item explicitly listed in the form: `https://dev-api.n-compass.online`
- Selected test surfaces: Web application, API, Device / hardware / IoT

## Scope Out

- The form does not list a clean explicit out-of-scope asset set beyond the unchecked or restricted categories below
- Literal entry present under `Please list anything that must NOT be tested:`
  - `Test all you want`

## Rules of Engagement

- **Testing window:** Preferred start date April 24, 2026, preferred end date May 1, 2026, timezone GMT+8
- **Allowed testing times:** Business hours, Flexible
- **Allowed techniques explicitly selected in the form:**
  - Security testing of the listed in-scope targets
  - Other: `Test anything you want`
- **Interpretation note:** the checked `Other` entry broadens the apparent allowance in the form, so the unchecked items in this section should not be treated too literally as hard prohibitions by default. In this engagement record, blanks or unchecked items are treated as not individually affirmed, not automatically disallowed, unless the form or later clarification says otherwise.
- **Specific allowed items not individually checked:**
  - Attempting to confirm real weaknesses safely
  - Using provided test accounts
  - Limited proof-of-access demonstration where needed
- **Separately approved / restricted section as written in the form:**
  - Denial of service or stress testing
  - Social engineering
  - Phishing
  - Physical testing
  - Testing third-party systems not explicitly listed
  - Accessing live customer content unless necessary
  - Any action that changes or deletes production data
- **DoS allowed?:** not individually checked, but the overall form language includes a broader `Other: Test anything you want` allowance, so treat this as requiring operator judgment rather than reading the blank alone as a hard `no`
- **Persistence allowed?:** not stated in the form
- **Social engineering allowed?:** not individually checked, but not automatically ruled out solely from the blank state under the user's intended interpretation
- **Third-party / cloud approvals:** third-party hosted systems are marked `Yes`, provider listed is `AWS`, and permission from those third parties if needed is marked `Yes`

## Safety Controls

- **Blackout periods:** none entered, only template example text appears in that field
- **Fragile systems / constraints:** the form says the most important things to protect are `Endpoint and Physical Access, Cloning of Image`
- **Emergency stop conditions:** not specified in the form
- **Resume authority:** not specified in the form

## Data Handling

- **Collection limits:** not specifically defined in the form
- **Storage expectations:** workspace engagement folders only
- **Retention / destruction:** not specified in the form
- **Sensitive data handling:** not specifically defined in the form

## Approval Status

- **Authorization confirmed?:** yes, the approver selected `Yes` for authorization confirmation
- **Provider approvals confirmed?:** yes, the form marks third-party permission as `Yes`
- **Cleared for reconnaissance now?:** yes
- **Cleared for active testing?:** yes, with broad allowance implied by the checked `Other: Test anything you want` entry, while still preserving the form's listed restricted categories and unanswered operational details as context rather than converting every blank into a denial
- **Current operating interpretation:** operator interprets the client's `Test anything you want` / `Test all you want` language as intended broad permission for the named target and selected surfaces, but will still treat destructive, stress, or otherwise high-impact actions conservatively until the ROE wording is tightened

## Notes

- Pre-engagement process detail for this engagement:
  - the user initiated the engagement through the `/pentest` workflow
  - the Assigned Penetration Tester information was collected as part of that intake path
  - a client-facing Google Doc pre-engagement form was spawned
  - the client completed the form
  - the filled form became the basis for this scope and ROE interpretation after ingestion
- Refreshed directly from the filled Google Doc pre-engagement form at `https://docs.google.com/document/d/1Msa0CrGZSOuyIciPtaeG6pkgWeo4ivYDQ7-5YC8vST4/edit`
- Ingestion method: `scripts/orchestration/ingest_pre_engagement_form.py` via `gog docs export --format md`
- Practical reproducibility note for this phase:
  - this ROE record comes from a spawned and later ingested Google Doc workflow, not a manually written one-off file
  - the operative path was intake workflow -> client form -> filled form -> export -> ingest -> local engagement docs
- This revision stays closer to the literal form values and distinguishes explicit selections from blanks, template examples, and ambiguous free text
- The form contains both `Test all you want` and `Other: Test anything you want`; in this analysis pass, the checked `Other` entry is treated as materially broadening the apparent authorization instead of letting unchecked boxes override it by default
- Operator decision for this phase gate: the current pre-engagement record is sufficient to proceed into recon under a low-risk, evidence-first posture
- Physical testing, emergency stop flow, escalation chain, and other high-impact ROE details remain incompletely specified, so those items should be treated cautiously until clarified
- Technical contact availability, emergency contact chain, and several operational fields remain unanswered in the source form
- Initialized by `scripts/orchestration/init_engagement_docs.py`
