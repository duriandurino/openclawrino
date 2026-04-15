#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime
import sys

SEVERITIES = {'Critical', 'High', 'Medium', 'Low', 'Informational'}

if len(sys.argv) < 3:
    print('Usage: python3 scripts/91-build-presentation-outline.py <findings.md> <slides.md>')
    sys.exit(1)

findings_path = Path(sys.argv[1])
slides_path = Path(sys.argv[2])
text = findings_path.read_text(encoding='utf-8') if findings_path.exists() else ''

findings = []
current = None
expect_title = False
expect_severity = False

for raw_line in text.splitlines():
    line = raw_line.strip()
    if raw_line.startswith('## Finding ID:'):
        if current:
            findings.append(current)
        current = {'id': raw_line.replace('## Finding ID:', '').strip(), 'title': 'Untitled', 'severity': 'TBD'}
        expect_title = False
        expect_severity = False
    elif current and raw_line.startswith('### Title'):
        expect_title = True
        expect_severity = False
    elif current and raw_line.startswith('### Severity'):
        expect_severity = True
        expect_title = False
    elif current and expect_title and line and not line.startswith('#'):
        current['title'] = line
        expect_title = False
    elif current and expect_severity and line in SEVERITIES:
        current['severity'] = line
        expect_severity = False
if current:
    findings.append(current)

counts = {sev: 0 for sev in ['Critical', 'High', 'Medium', 'Low', 'Informational']}
for item in findings:
    if item['severity'] in counts:
        counts[item['severity']] += 1

today = datetime.now().strftime('%Y-%m-%d')
lines = [
    '# Slide 1 - Player V2 Security Assessment',
    '- package: player-v2-direct',
    f'- date: {today}',
    '- mode: direct local assessment package and operator handoff',
    '',
    '# Slide 2 - Assessment Positioning',
    '- direct keyboard and mouse access on Raspberry Pi is the primary starting point',
    '- SSH and decryption material are not assumed',
    '- prior evidence favors local workflow review over blind remote probing',
    '',
    '# Slide 3 - Findings Summary'
]

if findings:
    for sev in ['Critical', 'High', 'Medium', 'Low', 'Informational']:
        if counts[sev]:
            lines.append(f'- {sev}: {counts[sev]}')
else:
    lines.append('- No parsed findings yet')

lines += [
    '',
    '# Slide 4 - Seeded Findings'
]

if findings:
    for item in findings:
        lines.append(f"- {item['id']}: {item['title']} ({item['severity']})")
else:
    lines.append('- Populate from reports/findings.md after validation')

lines += [
    '',
    '# Slide 5 - What Still Requires Live Validation',
    '- current device network posture',
    '- local startup chain and service mappings',
    '- any newly recovered secrets or artifact handling paths',
    '',
    '# Slide 6 - Remediation Priorities',
    '- document decrypt and recovery workflow',
    '- preserve artifact provenance and signed metadata',
    '- review privileged local startup and secret exposure paths',
    '',
    '# Slide 7 - Operator Next Steps',
    '- run the package scripts on the live Raspberry Pi',
    '- preserve hashes, screenshots, and logs',
    '- promote only revalidated items into the final report',
]

slides_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'[+] Wrote {slides_path}')
