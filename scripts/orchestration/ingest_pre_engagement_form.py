#!/usr/bin/env python3
"""Ingest a Google Docs pre-engagement form into structured JSON.

Preferred source order:
1. `gog docs export --format md` because it preserves checkbox/radio state as
   markdown task list markers like `[x]` and `[ ]`
2. `gog docs structure` as a fallback when markdown export is unavailable

The markdown path fixes the old failure mode where export-to-PDF/text or raw
structure views could lose selection state and force the workflow to treat many
answered fields as unknown.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


class IngestError(Exception):
    pass


def run_json(cmd: list[str]) -> Any:
    env = os.environ.copy()
    if not env.get("GOG_KEYRING_PASSWORD"):
        env["GOG_KEYRING_PASSWORD"] = "hatlesswhite"
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise IngestError((proc.stderr or proc.stdout).strip() or f"command failed: {' '.join(cmd)}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise IngestError(f"invalid JSON from {' '.join(cmd)}: {exc}") from exc


SECTION_HEADINGS = {
    "1. Organization and Approval": "organization_and_approval",
    "2. Why You Want This Test": "why_test",
    "3. What Needs to Be Tested": "scope",
    "4. Test Schedule": "schedule",
    "5. Access and Support": "access_and_support",
    "6. Sensitive or High-Risk Areas": "high_risk_areas",
    "7. Allowed and Not Allowed": "allowed_and_not_allowed",
    "8. Communication During the Test": "communication",
    "9. Report Expectations": "report_expectations",
    "10. Confirmation": "confirmation",
}

QUESTION_PREFIXES = (
    "Organization name:",
    "Primary contact person:",
    "Role / title:",
    "Email address:",
    "Phone number:",
    "Authorized approver name:",
    "Approver role / title:",
    "Approver email:",
    "Approver phone:",
    "I confirm that I am allowed to approve this testing on behalf of the organization:",
    "Approval reference:",
    "Approval date:",
    "Engagement title:",
    "Why are you requesting this test?",
    "What do you want this test to help you find or confirm?",
    "What is most important to protect?",
    "Which of these should be tested?",
    "System / application / project name(s):",
    "Main domain, URL, app name, IP range, or environment name:",
    "Please list the items that should be included in testing:",
    "Please list anything that must NOT be tested:",
    "Are any third-party hosted systems involved?(optional)",
    "If yes, who provides them?(optional)",
    "Do you already have permission from those third parties if needed?(optional)",
    "Preferred test start date:",
    "Preferred test end date:",
    "Timezone:",
    "When is testing allowed?",
    "Are there any dates or times when testing must NOT happen?",
    "Are there any deadlines for the report or results?",
    "If yes, what deadline?",
    "Will test accounts or credentials be provided?",
    "If yes, what kind?",
    "Please list them:",
    "Will a technical contact be available during testing in case questions or issues come up?",
    "Technical contact name:",
    "Are there systems or data that require extra care?",
    "If yes, please describe them:",
    "Are there systems where service interruption would be unacceptable?",
    "If yes, please list them:",
    "If something unexpected happens during testing, who should be contacted first?(optional)",
    "Please mark what is allowed for this engagement.",
    "How should important updates be sent?",
    "How often do you want progress updates?",
    "How should urgent or critical findings be reported?",
    "Who should receive the final report?",
    "What type of report would be most useful?",
    "Do you want a retest after fixes are made?",
    "I confirm that the information above is accurate to the best of my knowledge.",
    "I understand that authorized security testing can still carry some risk, including possible instability or service issues, and that safe timing, contacts, and limits must be followed.",
    "Name:",
)


def is_question_text(text: str) -> bool:
    return any(text.startswith(prefix) for prefix in QUESTION_PREFIXES)


MULTI_CHOICE_QUESTIONS = {
    "I confirm that I am allowed to approve this testing on behalf of the organization:",
    "Are any third-party hosted systems involved?(optional)",
    "Do you already have permission from those third parties if needed?(optional)",
    "When is testing allowed?",
    "Are there any deadlines for the report or results?",
    "Will test accounts or credentials be provided?",
    "If yes, what kind?",
    "Will a technical contact be available during testing in case questions or issues come up?",
    "Are there systems or data that require extra care?",
    "Are there systems where service interruption would be unacceptable?",
    "How should important updates be sent?",
    "How often do you want progress updates?",
    "How should urgent or critical findings be reported?",
    "What type of report would be most useful?",
    "Do you want a retest after fixes are made?",
    "I confirm that the information above is accurate to the best of my knowledge.",
    "I understand that authorized security testing can still carry some risk, including possible instability or service issues, and that safe timing, contacts, and limits must be followed.",
}


def normalize_text(value: str) -> str:
    return value.replace("\u000b", "\n").strip()


def parse_markdown(md_text: str) -> dict[str, Any]:
    sections: dict[str, list[dict[str, Any]]] = {"root": []}
    current_section = "root"
    lines = md_text.splitlines()
    i = 0

    def ensure_section(name: str) -> None:
        sections.setdefault(name, [])

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("## "):
            title = stripped[3:].replace("\\.", ".").strip()
            mapped = SECTION_HEADINGS.get(title)
            if mapped:
                current_section = mapped
            else:
                current_section = title.lower().replace(" ", "_")
            ensure_section(current_section)
            i += 1
            continue

        ensure_section(current_section)

        if stripped.startswith("### "):
            sections[current_section].append({"text": stripped[4:].strip(), "bullet": False})
            i += 1
            continue

        if stripped.startswith("**"):
            q = stripped.strip("*").replace("\\.", ".").strip()
            item: dict[str, Any] = {"question": q}
            selected = []
            options = []
            answers = []
            bullets = []
            j = i + 1
            while j < len(lines):
                raw = lines[j].rstrip()
                s = raw.strip()
                if not s:
                    j += 1
                    continue
                if s.startswith("## ") or s.startswith("### ") or s.startswith("**"):
                    break
                if s.startswith("- [x]") or s.startswith("* [x]"):
                    value = s.split("]", 1)[1].strip().replace("\\_", "_")
                    options.append(value)
                    selected.append(value)
                elif s.startswith("- [ ]") or s.startswith("* [ ]"):
                    value = s.split("]", 1)[1].strip().replace("\\_", "_")
                    options.append(value)
                elif s.startswith("- ") or s.startswith("* "):
                    value = s[2:].strip().replace("\\_", "_")
                    bullets.append(value)
                else:
                    answers.append(s.replace("\\.", ".").replace("\\_", "_"))
                j += 1

            if options:
                item["options_visible"] = options
                if len(selected) == 1:
                    item["selected"] = selected[0]
                elif len(selected) > 1:
                    item["selected"] = selected
                else:
                    item["selected"] = None
            if bullets:
                item["bullets"] = bullets
            if answers:
                item["answer"] = "\n".join(answers)
            sections[current_section].append(item)
            i = j
            continue

        sections[current_section].append({"text": stripped.replace("\\.", ".").replace("\\_", "_"), "bullet": stripped.startswith(("- ", "* "))})
        i += 1

    return {"sections": sections}


def parse_structure(paragraphs: list[dict[str, Any]]) -> dict[str, Any]:
    cleaned = []
    for p in paragraphs:
        text = normalize_text(p.get("text", ""))
        cleaned.append({
            "text": text,
            "bullet": bool(p.get("bullet")),
            "type": p.get("type"),
        })

    result: dict[str, Any] = {"sections": {}}
    current_section = "root"
    result["sections"][current_section] = []

    i = 0
    while i < len(cleaned):
        entry = cleaned[i]
        text = entry["text"]
        if text in SECTION_HEADINGS:
            current_section = SECTION_HEADINGS[text]
            result["sections"].setdefault(current_section, [])
            i += 1
            continue

        if not text:
            i += 1
            continue

        if is_question_text(text):
            item: dict[str, Any] = {"question": text}
            options: list[str] = []
            answers: list[str] = []
            j = i + 1
            while j < len(cleaned):
                nxt = cleaned[j]
                nxt_text = nxt["text"]
                if nxt_text in SECTION_HEADINGS or is_question_text(nxt_text):
                    break
                if nxt_text:
                    if nxt["bullet"]:
                        options.append(nxt_text)
                    else:
                        answers.append(nxt_text)
                j += 1

            if text in MULTI_CHOICE_QUESTIONS:
                item["options_visible"] = options
                item["selected"] = answers[0] if answers else None
                if len(answers) > 1:
                    item["extra_answers"] = answers[1:]
            else:
                if options:
                    item["bullets"] = options
                if answers:
                    item["answer"] = "\n".join(answers)

            result["sections"][current_section].append(item)
            i = j
            continue

        result["sections"][current_section].append({"text": text, "bullet": entry["bullet"]})
        i += 1

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc_id")
    parser.add_argument("--account", default="hatlesswhite@gmail.com")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    notes: list[str] = []
    method = None
    parsed = None

    try:
        env = os.environ.copy()
        if not env.get("GOG_KEYRING_PASSWORD"):
            env["GOG_KEYRING_PASSWORD"] = "hatlesswhite"
        with tempfile.TemporaryDirectory(prefix="preengage-md-") as tmpdir:
            out_path = Path(tmpdir) / "doc.md"
            proc = subprocess.run(
                [
                    "gog", "docs", "export", args.doc_id, "--account", args.account,
                    "--format", "md", "--output", str(out_path)
                ],
                capture_output=True,
                text=True,
                env=env,
            )
            if proc.returncode == 0 and out_path.exists() and out_path.read_text().strip():
                parsed = parse_markdown(out_path.read_text())
                method = "gog docs export --format md"
                notes.append("Markdown export preserved checkbox/radio state using [x]/[ ] markers.")
            else:
                notes.append("Markdown export unavailable, falling back to gog docs structure.")
    except Exception as exc:
        notes.append(f"Markdown export path failed, falling back to structure: {exc}")

    if parsed is None:
        structure = run_json([
            "gog", "docs", "structure", args.doc_id, "--account", args.account, "--json"
        ])
        parsed = parse_structure(structure.get("paragraphs", []))
        method = "gog docs structure"
        notes.append("Fallback structure parsing preserves visible options and free-text answers, but may lose explicit checkbox/radio state.")

    payload = {
        "ok": True,
        "docId": args.doc_id,
        "account": args.account,
        "method": method,
        "notes": notes,
        "parsed": parsed,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
