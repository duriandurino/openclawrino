#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: recon_whois_summary.sh --domain <domain> --engagement <name> [--base-dir <path>]
EOF
}

DOMAIN=""
ENGAGEMENT=""
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --domain) DOMAIN="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --base-dir) BASE_DIR="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -n "$DOMAIN" && -n "$ENGAGEMENT" ]] || { usage; exit 2; }
command -v whois >/dev/null 2>&1 || { echo "missing dependency: whois" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "recon", "recon-whois-summary", ${DOMAIN@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"

whois "$DOMAIN" > "$RAW_PATH" || true
python3 - <<PY
import json
from pathlib import Path
raw = Path(${RAW_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
interesting = []
keys = ('registrar', 'creation date', 'updated date', 'expiration date', 'name server', 'domain status', 'organization', 'country')
for line in raw.splitlines():
    stripped = line.strip()
    lower = stripped.lower()
    if ':' not in stripped:
        continue
    if any(lower.startswith(k) for k in keys):
        interesting.append(stripped)
payload = {
    'target': ${DOMAIN@Q},
    'phase': 'recon',
    'script': 'scripts/recon/whois/recon_whois_summary.sh',
    'status': 'success',
    'findings': [{'type': 'whois', 'value': item} for item in interesting],
    'artifacts': {'raw': ${RAW_PATH@Q}, 'parsed': ${PARSED_PATH@Q}, 'summary': ${SUMMARY_PATH@Q}}
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [f"# WHOIS Summary — ${DOMAIN}", '', f"- Engagement: ${ENGAGEMENT}", f"- Findings: {len(interesting)}", '', '## Highlights']
summary.extend([f"- {item}" for item in interesting[:25]] or ['- No structured WHOIS fields extracted'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
