#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: enum_webhook_basic.sh --target <host-or-url> --engagement <name> [--base-dir <path>] [--safe]
EOF
}

TARGET=""
ENGAGEMENT=""
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SAFE_MODE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --base-dir) BASE_DIR="$2"; shift 2 ;;
    --safe) SAFE_MODE=1; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -n "$TARGET" && -n "$ENGAGEMENT" ]] || { usage; exit 2; }
command -v curl >/dev/null 2>&1 || { echo "missing dependency: curl" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }

if [[ "$TARGET" =~ ^https?:// ]]; then
  BASE_URL="${TARGET%/}"
else
  BASE_URL="http://$TARGET"
fi

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "webhook-basic", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"

ENDPOINTS=("$BASE_URL/webhook" "$BASE_URL/webhooks" "$BASE_URL/api/webhook" "$BASE_URL/hooks" "$BASE_URL/callback")
{
  for endpoint in "${ENDPOINTS[@]}"; do
    echo "## HEAD $endpoint"
    curl -sk -I "$endpoint" || true
    echo
    echo "## OPTIONS $endpoint"
    curl -sk -i -X OPTIONS "$endpoint" || true
    echo
  done
} > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
raw = Path(${RAW_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
findings = []
endpoints = Path(${RAW_PATH@Q}).read_text(encoding='utf-8', errors='ignore').split('## HEAD ')
for block in endpoints:
    if not block.strip():
        continue
    first = block.splitlines()[0].strip()
    if ' 200 ' in block or ' 202 ' in block or ' 204 ' in block or ' 405 ' in block:
        findings.append({'type': 'webhook-endpoint', 'value': first})
if 'x-hub-signature' in raw.lower() or 'x-signature' in raw.lower() or 'stripe-signature' in raw.lower():
    findings.append({'type': 'signature', 'value': 'Webhook signature header indicators observed'})
if 'allow:' in raw.lower() and 'post' in raw.lower():
    findings.append({'type': 'method', 'value': 'POST appears allowed on one or more webhook-like endpoints'})
payload = {
    'target': ${TARGET@Q},
    'phase': 'enum',
    'script': 'scripts/enum/web/enum_webhook_basic.sh',
    'status': 'success',
    'safe_mode': bool(${SAFE_MODE}),
    'findings': findings,
    'artifacts': {
        'raw': ${RAW_PATH@Q},
        'parsed': ${PARSED_PATH@Q},
        'summary': ${SUMMARY_PATH@Q},
    }
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [
    f"# Webhook Basic Enum — ${TARGET}",
    '',
    '- Engagement: ${ENGAGEMENT}',
    f'- Base URL: ${BASE_URL}',
    f'- Safe mode: ${SAFE_MODE}',
    f'- Findings: {len(findings)}',
    '',
    '## Findings',
]
summary.extend([f"- {item['type']}: {item['value']}" for item in findings] or ['- No notable webhook findings captured'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
