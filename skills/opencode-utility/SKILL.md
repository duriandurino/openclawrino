---
name: opencode-utility
description: "Use OpenCode as a coding utility for authorized work. Use when: building scripts, refactoring helpers, planning or implementing reusable coding utilities, converting one-off commands into maintainable tools, or offloading scripting-heavy work during an engagement. NOT for: reasoning-only tasks, trivial shell use, non-coding pentest decisions, or unsafe/unauthorized offensive tooling such as malware, phishing kits, or credential theft tools."
metadata: {"openclaw": {"emoji": "🛠️"}}
---

# OpenCode Utility

Use OpenCode to offload scripting and coding work while keeping assessment logic, prioritization, and decision-making in the main agent.

## When to Use

✅ **USE this skill when:**
- "Use OpenCode to build a parser for this output"
- "Refactor this rough script into something reusable"
- "Plan the smallest useful helper before we code it"
- "Turn this one-liner into a maintainable CLI utility"
- A pentest phase needs coding, parsing, formatting, or automation glue
- The work is mostly implementation and coding would slow the operator down

## When NOT to Use

❌ **DON'T use this skill when:**
- The task is mostly reasoning, triage, prioritization, or interpreting findings
- A direct shell command is enough and no reusable code is needed
- The answer is trivial and can be given immediately without code generation
- The request would create unsafe or unauthorized tooling, including malware, phishing kits, credential theft tooling, destructive payloads, or indiscriminate attack automation

---

## Core Rule

Keep OpenCode in a support role.

The operator or phase agent decides:
- what problem needs code
- whether planning is needed first
- whether the output should be throwaway, session utility, or reusable utility
- whether the task is lawful and in scope

OpenCode handles the coding-heavy part.

## Safety Boundary

Use OpenCode only in support of authorized, legal work such as:
- lab environments
- owned systems
- approved client engagements
- defensive validation
- internal testing

Refuse unsafe or unauthorized requests. Stay inside approved scope.

## Default Preference

Prefer a MiniMax model in OpenCode when available and working well.

If MiniMax is unavailable or repeatedly produces weak output:
1. tighten the prompt once
2. retry once
3. fall back to another configured model

## Mode Selection

Choose the mode before invoking OpenCode.

### Use Plan Mode

Use plan mode when the code shape is still unclear.

Examples:
- decide between bash and Python
- scope the smallest useful utility
- redesign a messy helper before rewriting it
- figure out how reusable the tool should be
- debug why a script design is unreliable

Plan-mode objective:
- produce the smallest useful design
- define inputs, outputs, assumptions, and reuse level
- avoid building until the path is clear

### Use Build Mode

Use build mode when the coding target is already clear.

Examples:
- implement a parser or converter
- refactor a script into functions with argparse and logging
- build a reusable local CLI helper
- generate a project utility with sane defaults
- convert a rough snippet into maintainable code

Build-mode objective:
- produce working code quickly
- keep dependencies minimal
- make the result easy to inspect and reuse

### Hybrid Rule

For medium or large coding tasks:
1. use plan mode first
2. review the plan internally
3. use build mode to implement
4. summarize what was created and how to reuse it

## Reusability Bias

Prefer reusable scripts when the pattern is likely to recur.

Use these buckets:
- **throwaway** — urgent one-off helper
- **session utility** — useful within the current engagement
- **reusable utility** — likely valuable across future authorized work

Bias toward **reusable utility** for most scripting work, but do not overengineer tiny tasks.

Reusable upgrades can include:
- CLI arguments
- modular functions
- logging
- input validation
- clear outputs
- simple usage examples

## Workspace Organization

Save outputs in the workspace so they are part of repo history.

Preferred locations:

```text
scripts/opencode/throwaway/
scripts/opencode/session/
scripts/opencode/reusable/
```

Use these rules:
- save urgent one-off helpers to `scripts/opencode/throwaway/`
- save engagement-specific helpers to `scripts/opencode/session/`
- save generally useful tooling to `scripts/opencode/reusable/`
- add a short README or usage note only when the utility is not obvious
- keep filenames descriptive and stable

## Invocation Workflow

### Step 1 — Decide if OpenCode is justified

Use OpenCode only when code writing is the bottleneck.

Do not invoke it for:
- tiny answers
- obvious shell commands
- repeated vague brainstorming with no coding target

### Step 2 — Pick the utility class

Choose one:
- throwaway
- session utility
- reusable utility

Default to **reusable utility** when the same pattern will likely recur.

### Step 3 — Pick the mode

Choose:
- **plan** if the shape is unclear
- **build** if code is needed now
- **plan → build** for medium or large work

### Step 4 — Use a focused prompt

Prefer prompts that are narrow, explicit, and dependency-light.

Plan prompt shape:

```text
Analyze this coding task for an authorized security workflow. Prefer MiniMax. Do not build yet unless absolutely necessary. Propose the smallest useful utility design, suggested language, structure, inputs, outputs, reusability level, and any risks or assumptions.
```

Build prompt shape:

```text
Build this coding utility for an authorized security workflow. Prefer MiniMax. Make it minimal but practical, preserve simplicity, avoid unnecessary dependencies, and provide a concise summary of what was created, expected inputs, outputs, and how it can be reused.
```

### Step 5 — Save and review the result

Before adopting the output:
- verify it matches the scope
- check for unsafe behavior
- confirm the dependency footprint is reasonable
- place it in the correct `scripts/opencode/` bucket
- run a basic sanity test where appropriate

## Phase-Agent Guidance

Phase agents should use this skill only when the phase requires coding or scripting support.

Good fits:
- recon result normalizers
- enum output parsers
- vuln evidence formatters
- exploit-lab helper scripts for authorized validation
- post-exploitation note converters for authorized reporting
- reporting helpers that turn notes into structured markdown

Bad fits:
- replacing phase judgment
- deciding exploit paths
- writing unauthorized offensive tooling
- avoiding direct manual verification when simple checks are enough

## Reporting Back After Use

After using OpenCode, report briefly:
- mode used: plan or build
- why that mode was chosen
- what was planned or created
- utility class: throwaway, session, or reusable
- assumptions or limitations

## Local Prep Notes

For CLI verification and OpenCode workspace assumptions, see `references/opencode-cli-notes.md`.
