#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: winrm_probe.sh --target <host> --engagement <name> [--base-dir <path>]
EOF
}

TARGET=""
ENGAGEMENT=""
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --base-dir) BASE_DIR="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -n "$TARGET" && -n "$ENGAGEMENT" ]] || { usage; exit 2; }
command -v nmap >/dev/null 2>&1 || { echo "missing dependency: nmap" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "winrm-probe", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"

nmap -Pn -p 5985,5986 -sV "$TARGET" -oN "$RAW_PATH" >/dev/null 2>&1 || true
python3 - <<PY
import json
from pathlib import Path
text = Path(${RAW_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
findings = []
for port in ('5985/tcp open', '5986/tcp open'):
    if port in text:
        findings.append({'type': 'winrm', 'value': port})
payload = {
  'target': ${TARGET@Q},
  'phase': 'enum',
  'script': 'scripts/enum/winrm/winrm_probe.sh',
  'status': 'success',
  'findings': findings,
  'artifacts': {'raw': ${RAW_PATH@Q}, 'parsed': ${PARSED_PATH@Q}, 'summary': ${SUMMARY_PATH@Q}}
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [f"# WinRM Probe — ${TARGET}", '', f"- Engagement: ${ENGAGEMENT}", f"- Findings: {len(findings)}"]
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
