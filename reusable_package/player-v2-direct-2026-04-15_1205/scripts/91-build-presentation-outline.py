#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) < 3:
    print('Usage: python3 scripts/91-build-presentation-outline.py <findings.md> <slides.md>')
    sys.exit(1)

findings_path = Path(sys.argv[1])
slides_path = Path(sys.argv[2])
text = findings_path.read_text(encoding='utf-8') if findings_path.exists() else ''

findings = []
current = None
for line in text.splitlines():
    if line.startswith('## Finding ID:'):
        if current:
            findings.append(current)
        current = {'id': line.replace('## Finding ID:', '').strip(), 'title': 'Untitled', 'severity': 'TBD'}
    elif current and line.startswith('### Title'):
        continue
    elif current and current.get('title') == 'Untitled' and line.strip() and not line.startswith('#'):
        current['title'] = line.strip()
    elif current and line.startswith('### Severity'):
        continue
    elif current and current.get('severity') == 'TBD' and line.strip() in {'Critical', 'High', 'Medium', 'Low', 'Informational'}:
        current['severity'] = line.strip()
if current:
    findings.append(current)

lines = [
    '# Slide 1 - Player V2 Security Assessment',
    '- engagement title',
    '- date',
    '',
    '# Slide 2 - Findings Overview'
]

if findings:
    for item in findings:
        lines.append(f"- {item['id']}: {item['title']} ({item['severity']})")
else:
    lines.append('- No parsed findings yet, populate from reports/findings.md')

lines += [
    '',
    '# Slide 3 - Remediation Priorities',
    '- immediate fixes',
    '- hardening tasks',
    '- follow-up validation',
]

slides_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'[+] Wrote {slides_path}')