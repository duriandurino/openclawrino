---
name: presentation
description: "Generate pentest presentation slides from engagement findings. Use when: user asks for slides, presentation deck, slide count specified, 'make a presentation', 'create slides', or wants a talk/showcase format from pentest reports. NOT for: writing the full technical report (use reporting skill), raw data collection, or non-security presentations."
---

# Presentation Skill

Generate structured presentation slides from pentest engagement data.

## When to Use

✅ **USE this skill when:**
- "Give me 10 slides for this pentest"
- "Create a presentation from the report"
- "I need 5 slides for management"
- "Generate slides with speaker notes"
- User specifies a slide count
- User mentions "presentation", "deck", "slides", "showcase"

## When NOT to Use

❌ **DON'T use this skill when:**
- Writing the full technical report (use `reporting` skill)
- Raw data collection or scan output
- Non-security presentations
- User wants a document, not a visual deck

---

## Slide Structure

### Default Template (Adapts to Slide Count)

Every slide deck follows this flow. Slide density adjusts to the requested count:

```
Slide 1:  Title Slide
Slide 2:  Executive Summary / Problem Statement
Slide 3:  Scope, ROE, Target Overview
Slide 4:  Attack Path / Engagement Story
[Slides 5-N-3: Findings (distributed by severity and status)]
Slide N-2: Remediation + Retest Roadmap
Slide N-1: Why OpenClaw / Methodology Value
Slide N:   Cleanup, Residual Risk, Q&A / Contact
```

### Slide Distribution by Count

| Total Slides | Exec/Problem | Scope/Target | Attack Path | Findings | Remediation | Methodology | Closing |
|-------------|--------------|--------------|-------------|----------|-------------|-------------|---------|
| **5** | 1 | 1 | 0 | 2 | 1 | 0 | 1 |
| **7** | 1 | 1 | 1 | 3 | 1 | 0 | 1 |
| **10** | 1 | 1 | 1 | 5 | 1 | 1 | 1 |
| **12** | 1 | 1 | 1 | 6 | 1 | 1 | 1 |
| **15** | 1 | 1 | 1 | 8 | 2 | 1 | 1 |
| **20** | 2 | 1 | 2 | 11 | 2 | 1 | 1 |

---

## Slide Format

Each slide output follows this structure:

```
### SLIDE [N]: [Title]

**Visual:** [Description of what to show — diagram, table, bullet list, screenshot reference]

**Content:**
- Bullet point 1
- Bullet point 2
- Bullet point 3

**Speaker Notes:**
What the presenter should say while this slide is shown.

**Transition:** [One-line cue to next slide]
```

---

## Finding Slide Templates

### Single Finding Slide

```
### SLIDE [N]: Finding — [Title]

**Visual:** Severity badge + CVSS score + icon

**Content:**
- **Severity:** [CRITICAL/HIGH/MEDIUM/LOW] (CVSS X.X if used)
- **Status:** [suspected / validated / exploited / retested]
- **Affected:** [Target/service/version]
- **What:** [1-line vulnerability description]
- **Impact:** [1-line business impact]
- **Evidence:** [EVI-XXX or concise proof reference]

**Speaker Notes:**
[Talking points with context, evidence reference]

**Demo Cue:** [If applicable — "Show terminal output #X"]
```

### Findings Summary Slide (Multiple Findings)

```
### SLIDE [N]: Key Findings Summary

**Visual:** Table or matrix

**Content:**
| # | Finding | Severity |
|---|---------|----------|
| 1 | [Title] | [Severity] |
| 2 | [Title] | [Severity] |
| ... | ... | ... |

**Speaker Notes:**
[Brief walkthrough of each finding]
```

### Attack Chain Slide

```
### SLIDE [N]: Attack Chain / Engagement Story

**Visual:** Flowchart, timeline, or attack-path table

**Content:**
[Step 1] → [Step 2] → [Step 3] → [Result]
Each step with brief label, and include evidence IDs where possible

**Speaker Notes:**
[Narrative walkthrough of the exploitation path or blocked path]
```

---

## Data Sources

Read from the engagement report directory:

```
engagements/<target>/06-report/
├── REPORT_FINAL_<timestamp>.md            # Primary source for all content
├── EXECUTIVE_SUMMARY_<timestamp>.md       # Executive framing if split out
├── presentation-ready.md                  # Optional prepared deck source
└── openclaw-value.md                      # Methodology/why OpenClaw content
```

Also read from shared registers and phase directories for evidence references:

```
engagements/<target>/registers/
engagements/<target>/{01-recon,02-enum,03-vuln,04-exploit,05-post-exploit}/
```

---

## Presentation Styles

### Style: Executive (Non-Technical)
- Minimal jargon, focus on business impact
- Emphasize financial/reputational risk
- Remediation as investment, not fix
- Skip CVSS scores, use color-coded risk labels

### Style: Technical (Engineers/IT)
- Include CVSS scores and CVE IDs
- Show terminal commands and outputs
- Detail the exploit chain
- Include code snippets and config changes

### Style: Mixed Audience
- Findings as summary + one deep-dive
- Business impact first, technical detail optional
- Include "What happened" + "How we fixed it"

Default: **Mixed Audience** unless specified.

---

## Slide Generation Workflow

### Step 1 — Identify Slide Count
Extract the number from the user's request: "10 slides" → N=10

### Step 2 — Read Source Data
```
Read: engagements/<target>/report/findings-summary.md
Read: engagements/<target>/report/pentest-report-presentation.md
Read: engagements/<target>/report/openclaw-value.md
```

### Step 3 — Distribute Slides
Use the distribution table above to allocate slides per section.

### Step 4 — Generate Slides
Output each slide in the format above. Prioritize:
1. CRITICAL/HIGH findings first
2. Attack paths that explain business impact
3. Findings with strongest evidence and clearest remediation
4. Visual variety (mix tables, diagrams, bullets)

### Step 5 — Add Speaker Notes
Every slide must have speaker notes. These are what the presenter reads/speaks.

### Step 6 — Reflect Current Output Contract
Ensure the deck visibly covers:
- executive risk posture
- scope/ROE and limitations
- attack path or engagement story
- finding status and evidence
- remediation roadmap
- retest signal
- cleanup / residual risk

---

## Output File Naming Convention

All generated presentation files MUST include a datetime stamp for easy identification:

```
<DESCRIPTION>_<YYYY-MM-DD_HHMM>.md
```

Examples:
- `FINAL_5_slide_2026-03-17_1747.md`
- `FINAL_SUGGEST_slide_2026-03-17_1749.md`
- `KEY_TAKEAWAYS_2026-03-17_1749.md`
- `SLIDES_10_2026-03-18_0930.md`

This allows multiple versions to coexist and makes it easy to identify which is latest.

Get current datetime from session context or use `date +%Y-%m-%d_%H%M` if available.

## Output Format

Save to: `engagements/<target>/report/<DESCRIPTION>_<YYYY-MM-DD_HHMM>.md`

Present slides as numbered sections in the response. For each slide:

1. **Slide title** (what goes on the slide)
2. **Visual element** (what to show — table, diagram, bullets)
3. **Key points** (3-5 bullets max per slide)
4. **Speaker notes** (what to say)
5. **Demo/transition cue** (optional — when to show terminal or move)

---

## Customization Options

User can specify:
- **Slide count:** "Give me 10 slides" → adjusts density
- **Audience:** "for management" / "for technical team" → adjusts language
- **Focus:** "focus on the exploit chain" → prioritizes findings slides
- **Include/exclude:** "skip the methodology slides" / "add more on remediation"
- **With/without notes:** "with speaker notes" / "just the slide content"

---

## References

For detailed examples of each slide type, see `references/examples.md`.
For slide visual templates (ASCII diagrams), see `references/templates.md`.
