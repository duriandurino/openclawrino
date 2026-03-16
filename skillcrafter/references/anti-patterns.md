# Anti-Patterns — What Makes a Skill Bad

Every anti-pattern below has been observed in real skills. Avoid them all.

## 1. The Encyclopedia

**Symptom:** Explains the domain before showing how to do anything.

```markdown
# PDF Processing

PDF (Portable Document Format) was created by Adobe in 1993. It is a file format
that preserves document formatting across platforms. PDFs can contain text, images,
and vector graphics...

## Merging PDFs
```

**Fix:** Kill the intro. Start with the task:
```markdown
# PDF Processing

## When to Use
✅ "Merge these PDFs" | "Extract text from a PDF" | "Split this PDF at page 5"

## Merge PDFs

```bash
python3 scripts/merge.py file1.pdf file2.pdf -o merged.pdf
```
```

---

## 2. The Mystery Skill

**Symptom:** Description doesn't say what it does or when to trigger.

```yaml
description: "A utility for file operations"
```

**Fix:** Specific triggers + exclusions:
```yaml
description: "Convert between image formats (PNG, JPEG, WebP, SVG). Use when: user wants to resize, convert, crop, or compress images. NOT for: creating new images from scratch, photo editing with layers, or batch watermarking."
```

---

## 3. The Code Dump

**Symptom:** SKILL.md contains 100+ lines of inline code that belongs in `scripts/`.

```markdown
## Process Data

```python
import csv
import json
from collections import defaultdict

def process_csv(filepath):
    with open(filepath) as f:
        reader = csv.DictReader(f)
        results = defaultdict(list)
        for row in reader:
            results[row['category']].append(float(row['value']))
    return {k: sum(v) for k, v in results.items()}
# ... 50 more lines
```
```

**Fix:** Move to a script file and reference it:
```markdown
## Process Data

```bash
python3 scripts/process_data.py data.csv --group-by category
```

Script accepts: `--group-by`, `--output json|csv`, `--filter "column=value"`
```

---

## 4. The Hidden Reference

**Symptom:** Mentions external docs with no way to find them.

```markdown
For advanced options, consult the API documentation.
```

**Fix:** Either include the info or provide a concrete reference:
```markdown
For advanced options, see `references/api.md#advanced-options` (loaded on demand).
```

---

## 5. The Wishy-Washy Trigger

**Symptom:** Description doesn't tell the agent when to activate.

```yaml
description: "Helpful skills for common tasks"
```
```markdown
## When to Use
- When you need this skill
```

**Fix:** Exact phrases and contexts:
```yaml
description: "Generate and validate QR codes. Use when: user asks for a QR code, needs to encode a URL/text/phone number as QR, or wants to verify an existing QR code image. NOT for: barcodes (use barcode skill), image manipulation, or URL shortening."
```

---

## 6. The Wall of Text

**Symptom:** SKILL.md is 800+ lines with no structure or references split.

**Fix:** Apply progressive disclosure:
- Core workflow stays in SKILL.md (≤500 lines)
- Detailed examples → `references/examples.md`
- Variant-specific info → `references/<variant>.md`
- Long reference docs → `references/<topic>.md` with grep patterns in SKILL.md

---

## 7. The Dead Link

**Symptom:** SKILL.md references a file that doesn't exist.

```markdown
See `references/schema.md` for table definitions.
```
But `schema.md` was never created.

**Fix:** Phase 3 validation catches this. Always run:
```bash
python3 skillcrafter/scripts/validate_skill.py <skill-directory>
```

---

## 8. The Copy-Paste Skill

**Symptom:** SKILL.md is 90% copied from another skill's SKILL.md with the name changed.

**Fix:** Skills should reflect the actual tool/workflow. Tailor every section to the real commands, real APIs, real constraints of the domain.

---

## 9. The Missing Not-When

**Symptom:** Tells the agent when to use the skill but not when to avoid it.

```markdown
## When to Use
✅ "Convert this file" | "Transform the image"
```

Without exclusions, the agent may misfire on similar requests handled better by other tools.

**Fix:** Always include NOT-When:
```markdown
## When NOT to Use
❌ "Convert SVG to PDF" (use svg skill) | "Edit the image content" (use image-editor skill)
```

---

## 10. The Orphan Resource

**Symptom:** A file exists in `scripts/` or `references/` but is never mentioned in SKILL.md.

**Fix:** If a resource isn't referenced, it's dead weight. Either reference it or delete it.

---

## Quick Self-Check

After writing a skill, ask:

| Question | If no → |
|---|---|
| Would a user trigger this within 5 seconds? | Rewrite the description |
| Is every code block copy-pasteable? | Fix the examples |
| Did I validate with `validate_skill.py`? | Run it now |
| Does SKILL.md reference every file in the skill? | Add references or delete orphans |
| Is SKILL.md ≤500 lines? | Split to references/ |
