---
name: skillcrafter
description: "Strict, example-driven skill authoring for OpenClaw. Use when creating a new skill from scratch, improving an existing skill's quality, or auditing a skill against quality standards. Triggers on: create a skill, author a skill, improve this skill, review the skill, audit this skill, make a skill better, why isn't this skill working, skill quality check. Unlike the basic skill-creator, skillcrafter enforces strict quality gates, requires concrete usage examples, validates progressive disclosure, and rejects anti-patterns."
---

# Skillcraft — Strict Skill Authoring

Produce high-quality OpenClaw skills. Every skill passes through 5 phases. No shortcuts.

## Phase 0 — Gather Concrete Examples

**Do NOT skip this.** A skill without concrete usage examples is a guess, not a skill.

Ask or research: what will users actually say that should trigger this skill?
Collect 3–8 real phrases. If you can't think of any, you don't understand the domain yet.

**Good examples are specific:**
- ✅ "Rotate this PDF 90 degrees clockwise"
- ✅ "Convert my WAV recording to MP3"
- ❌ "Do PDF stuff" (too vague)
- ❌ "Help with files" (meaningless)

Store examples in `references/examples.md` for the skill to reference.

## Phase 1 — Plan Resources (Before Writing SKILL.md)

Analyze each example. For each, ask: **"What code or data would I re-write every time?"**

| Repeated work? | Resource to create |
|---|---|
| Same script code rewritten | A Python/shell script in `scripts/` |
| Same reference/docs looked up | A markdown file in `references/` |
| Same boilerplate/template output | A template directory in `assets/` |

If no resources are needed, that's fine. **Never create a resource just to fill a directory.**

## Phase 2 — Write SKILL.md

### Frontmatter (Strict Rules)

```yaml
---
name: hyphen-case-name          # REQUIRED — lowercase, hyphens, ≤64 chars
description: "..."              # REQUIRED — ≤1024 chars, no angle brackets, triggers + scope
---
```

**Description quality gate** — every description must answer:
1. What does this skill do? (1 sentence)
2. When should the agent use it? (specific triggers)
3. When should the agent NOT use it? (explicit exclusions)

Optional frontmatter fields:
```yaml
metadata:                    # Optional — tool requirements, emoji
  { "openclaw": { "emoji": "☔", "os": ["darwin", "linux"], "requires": { "bins": ["curl"] } } }
```

**Bad description:**
> "A skill for working with documents"

**Good description:**
> "Create, edit, and analyze PDF documents. Use when: extracting text from PDFs, merging/splitting PDFs, filling forms, or converting PDF formats. NOT for: creating new documents from scratch (use docx skill), viewing PDFs visually, or OCR on scanned images."

### Body Structure

Choose ONE structure pattern, then follow it:

**Task-based** (most common): For skills with distinct operations.
```markdown
# Skill Name

## [Primary Task 1]
[Instructions + example commands]

## [Primary Task 2]
[Instructions + example commands]
```

**Workflow-based**: For sequential multi-step processes.
```markdown
# Skill Name

## Step 1 — [Action]
## Step 2 — [Action]
## Step 3 — [Action]
```

**Reference-based**: For standards/guidelines.
```markdown
# Skill Name

## Principle 1
## Principle 2
## Specification
```

### Writing Rules

1. **Imperative mood** — "Extract text", not "To extract text" or "You can extract text"
2. **One blank line between sections** — not two, not zero
3. **Code blocks for every command** — never describe a command without showing it
4. **No filler explanations** — the agent is smart; don't explain what `curl` is
5. **≤500 lines total** — split to `references/` when approaching this limit
6. **When/Not-When section** — mandatory, placed near the top

### Progressive Disclosure (When SKILL.md Gets Too Long)

Keep SKILL.md lean. Move content out when approaching 500 lines:

| Content type | Where it goes |
|---|---|
| Variant-specific details (AWS vs GCP vs Azure) | `references/<variant>.md` (e.g. references/aws-example.md) |
| Detailed examples or reference docs | `references/<topic>.md` (e.g. references/api-ref.md) |
| Long API schemas or data dictionaries | `references/<topic>.md` with grep hints in SKILL.md |
| Templates, boilerplate, font files | `assets/` |

Link references directly from SKILL.md: "For X details, see `references/<x-details>.md` (loaded on demand)."
All references should be ≤1 level deep from SKILL.md — no nested linking.

### When/Not-When Format (Required)

```markdown
## When to Use

✅ **USE this skill when:**
- "User phrase that triggers it"
- Another trigger phrase
- File type or context that needs this skill

## When NOT to Use

❌ **DON'T use this skill when:**
- Alternative tool/ skill handles it
- Out-of-scope scenario
```

## Phase 3 — Validate

Run validation before packaging. Fix ALL issues.

```bash
python3 skillcrafter/scripts/validate_skill.py <skill-directory>
```

Checks enforced:
- Frontmatter has `name` and `description`
- Name: hyphen-case, ≤64 chars, no consecutive hyphens
- Description: ≤1024 chars, no angle brackets, has triggers
- SKILL.md body exists and is non-empty
- When/Not-When section present
- No banned files (README.md, CHANGELOG.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md)
- Referenced scripts exist and are executable
- Referenced files in body actually exist on disk

## Phase 4 — Package

Only after validation passes:

```bash
python3 skillcrafter/scripts/package_skill.py <skill-directory> [output-dir]
```

Creates `<skill-name>.skill` (zip archive) if all checks pass.

## Quality Checklist

Before considering a skill "done", verify:

- A user would trigger this skill within 5 seconds of reading the description
- Every code block is copy-pasteable and works
- No leftover placeholders in the skill
- Every referenced file exists
- Examples cover the main use cases
- Skill is self-contained (no missing context from external docs)
- ≤500 lines in SKILL.md (references/ for overflow)

## Anti-Patterns — Never Do These

See `references/anti-patterns.md` for full list with examples. Common violations:

1. **The Encyclopedia** — Explaining what PDF is before showing how to merge one
2. **The Mystery Skill** — Description says "A helper tool" with no context
3. **The Code Dump** — 200 lines of code in SKILL.md that belongs in scripts/
4. **The Hidden Reference** — "See the API docs" with no link or path
5. **The Wishy-Washy Trigger** — "Use when needed" is not a trigger

## Bundled Scripts

- `scripts/validate_skill.py` — Pre-packaging quality validation
- `scripts/package_skill.py` — Package validated skill into .skill file
- `scripts/init_skill.py` — Initialize new skill directory (from skill-creator)
