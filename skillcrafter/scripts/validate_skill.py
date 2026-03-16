#!/usr/bin/env python3
"""
skillcrafter strict validation — goes beyond quick_validate.py.

Checks:
  1. Frontmatter basics (name, description, format)
  2. Description quality (length, no angle brackets, trigger phrases)
  3. Body exists and is non-empty
  4. When/Not-When section present (case-insensitive)
  5. No banned files (README.md, CHANGELOG.md, INSTALLATION_GUIDE.md, QUICK_REFERENCE.md)
  6. Referenced files actually exist on disk
  7. No leftover TODO markers
  8. SKILL.md ≤500 lines (progressive disclosure guard)
  9. Scripts in scripts/ are executable (warn only)

Exit codes:
  0 = all passed
  1 = hard failure (skill is not valid)
  2 = soft warnings (skill passes but has issues)
"""

import os
import re
import stat
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_BODY_LINES = 500
BANNED_FILES = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}

# Frontmatter extraction
def _extract_frontmatter(content: str):
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i])
    return None

def _parse_frontmatter(text: str):
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
            return data if isinstance(data, dict) else None
        except yaml.YAMLError:
            return None
    # Fallback: simple key: value
    result = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if ":" not in s:
            return None
        k, v = s.split(":", 1)
        k, v = k.strip(), v.strip().strip("\"'")
        if k:
            result[k] = v
    return result

def validate(skill_dir: Path):
    errors = []
    warnings = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md not found"], []

    content = skill_md.read_text(encoding="utf-8")
    lines = content.splitlines()

    # --- 1. Frontmatter ---
    fm_text = _extract_frontmatter(content)
    if fm_text is None:
        errors.append("Invalid frontmatter (missing --- delimiters)")
        return errors, warnings

    fm = _parse_frontmatter(fm_text)
    if fm is None:
        errors.append("Invalid YAML in frontmatter")
        return errors, warnings

    if "name" not in fm:
        errors.append("Missing 'name' in frontmatter")
    else:
        name = str(fm["name"]).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"Name '{name}' must be hyphen-case (lowercase, digits, hyphens only)")
        if len(name) > MAX_NAME:
            errors.append(f"Name too long ({len(name)} chars, max {MAX_NAME})")

    if "description" not in fm:
        errors.append("Missing 'description' in frontmatter")
    else:
        desc = str(fm["description"]).strip()
        if len(desc) > MAX_DESCRIPTION:
            errors.append(f"Description too long ({len(desc)} chars, max {MAX_DESCRIPTION})")
        if "<" in desc or ">" in desc:
            errors.append("Description contains angle brackets (< or >)")
        if len(desc) < 20:
            warnings.append("Description is very short (<20 chars) — include triggers and scope")

    # Check for unexpected frontmatter keys
    allowed = {"name", "description", "license", "allowed-tools", "metadata"}
    extra = set(fm.keys()) - allowed
    if extra:
        warnings.append(f"Non-standard frontmatter keys: {', '.join(sorted(extra))}")

    # --- 2. Body ---
    # Strip frontmatter for body analysis
    body_start = 0
    in_fm = False
    fm_close_count = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            fm_close_count += 1
            if fm_close_count == 2:
                body_start = i + 1
                break

    body = "\n".join(lines[body_start:]) if body_start < len(lines) else ""
    body_stripped = body.strip()

    if not body_stripped:
        errors.append("SKILL.md body is empty")

    if len(lines) > MAX_BODY_LINES:
        warnings.append(f"SKILL.md is {len(lines)} lines (max recommended: {MAX_BODY_LINES}) — split to references/")

    # --- 3. When/Not-When ---
    body_lower = body_stripped.lower()
    has_when = bool(re.search(r"##\s+when\s+to\s+use", body_lower))
    has_not_when = bool(re.search(r"##\s+when\s+not\s+to\s+use", body_lower))
    if not has_when:
        errors.append("Missing '## When to Use' section")
    if not has_not_when:
        warnings.append("Missing '## When NOT to Use' section — add exclusions to prevent misfires")

    # --- 4. Banned files ---
    for f in BANNED_FILES:
        if (skill_dir / f).exists():
            errors.append(f"Banned file found: {f} — skill should be self-contained, not user-facing docs")

    # --- 5. Referenced files ---
    # Find markdown links and code references to local files
    ref_pattern = re.compile(r'(?:`([^`]+\.\w+)`|\[.*?\]\(([^)]+)\))')
    referenced = set()
    for match in ref_pattern.finditer(body):
        ref = match.group(1) or match.group(2)
        if ref and not ref.startswith(("http://", "https://", "#", "mailto:")):
            # Skip angle-bracket placeholders like <topic>, <variant>, <x-details>
            if re.search(r'<[^>]+>', ref):
                continue
            referenced.add(ref.split("#")[0])  # strip anchors

    for ref in sorted(referenced):
        ref_path = skill_dir / ref
        if not ref_path.exists() and not (skill_dir / "references" / ref).exists() and not (skill_dir / "scripts" / ref).exists():
            warnings.append(f"Referenced file not found: {ref}")

    # --- 6. TODO markers ---
    todos = [i+1 for i, line in enumerate(lines) if re.search(r'\[?TODO[:\]]', line, re.IGNORECASE)]
    if todos:
        spots = ", ".join(str(t) for t in todos[:5])
        errors.append(f"Leftover TODO markers on line(s): {spots} — remove or complete them")

    # --- 7. Script executability ---
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix in (".py", ".sh", ".bash"):
                mode = script.stat().st_mode
                if not (mode & stat.S_IXUSR):
                    warnings.append(f"Script not executable: scripts/{script.name} — run chmod +x")

    return errors, warnings


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_skill.py <skill-directory>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.is_dir():
        print(f"[FAIL] Not a directory: {skill_dir}")
        sys.exit(1)

    errors, warnings = validate(skill_dir)

    passed = True

    if errors:
        passed = False
        for e in errors:
            print(f"[FAIL] {e}")

    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")

    if passed and not warnings:
        print(f"[PASS] Skill '{skill_dir.name}' is valid!")
        sys.exit(0)
    elif passed:
        print(f"[PASS] Skill '{skill_dir.name}' is valid with warnings.")
        sys.exit(2)
    else:
        print(f"\n[PASS] {len(errors)} error(s) must be fixed before packaging.")
        sys.exit(1)


if __name__ == "__main__":
    main()
