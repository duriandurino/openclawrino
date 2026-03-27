#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: vuln_nestjs_baseline.sh --target <host-or-url> --engagement <name> [--base-dir <path>] [--safe]
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
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "vuln", "nestjs-baseline", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"

ENDPOINTS=("$BASE_URL" "$BASE_URL/swagger-json" "$BASE_URL/api-json" "$BASE_URL/openapi.json")
{
  for endpoint in "${ENDPOINTS[@]}"; do
    echo "## GET $endpoint"
    curl -sk -i "$endpoint" || true
    echo
    if [[ "$SAFE_MODE" -eq 0 ]]; then
      echo "## OPTIONS $endpoint"
      curl -sk -i -X OPTIONS "$endpoint" || true
      echo
    fi
  done
} > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
raw = Path(${RAW_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
lower = raw.lower()
findings = []
if 'swagger' in lower or 'openapi' in lower:
    findings.append({'type': 'nestjs', 'candidate': 'Swagger/OpenAPI documentation appears exposed', 'confidence': 'candidate'})
if 'access-control-allow-origin: *' in lower:
    findings.append({'type': 'nestjs', 'candidate': 'Wildcard CORS observed on API responses', 'confidence': 'candidate'})
if 'x-powered-by: express' in lower:
    findings.append({'type': 'nestjs', 'candidate': 'Express/NestJS server banner exposed', 'confidence': 'observed'})
if 'validationpipe' not in lower and ('nestjs' in lower or 'swagger' in lower or 'openapi' in lower):
    findings.append({'type': 'nestjs', 'candidate': 'No obvious NestJS validation indicators observed; confirm validation and DTO enforcement manually', 'confidence': 'candidate'})
if 'allow:' in lower and any(method in raw for method in ['PUT', 'DELETE', 'PATCH']):
    findings.append({'type': 'nestjs', 'candidate': 'Potentially risky HTTP methods exposed; confirm auth/guard coverage on write operations', 'confidence': 'candidate'})
payload = {
    'target': ${TARGET@Q},
    'phase': 'vuln',
    'script': 'scripts/vuln/web/vuln_nestjs_baseline.sh',
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
    f"# NestJS Baseline — ${TARGET}",
    '',
    '- Engagement: ${ENGAGEMENT}',
    f'- Base URL: ${BASE_URL}',
    f'- Safe mode: ${SAFE_MODE}',
    f'- Candidate findings: {len(findings)}',
    '',
    '## Findings',
]
summary.extend([f"- [{item['confidence']}] {item['candidate']}" for item in findings] or ['- No notable NestJS baseline findings captured'])
summary.append('')
summary.append('## Notes')
summary.append('- These are baseline NestJS/API observations only and require manual validation before reporting as confirmed findings.')
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
