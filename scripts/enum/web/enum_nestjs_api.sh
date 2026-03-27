#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: enum_nestjs_api.sh --target <host-or-url> --engagement <name> [--base-dir <path>] [--safe]
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
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "nestjs-api", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
SWAGGER_PATH="${RAW_PATH%.txt}-swagger.json"

PATHS_TO_CHECK=("$BASE_URL" "$BASE_URL/api" "$BASE_URL/swagger-json" "$BASE_URL/swagger" "$BASE_URL/api-json" "$BASE_URL/openapi.json")
{
  for endpoint in "${PATHS_TO_CHECK[@]}"; do
    echo "## $endpoint"
    curl -sk -i "$endpoint" || true
    echo
  done
} > "$RAW_PATH"

for endpoint in "$BASE_URL/swagger-json" "$BASE_URL/api-json" "$BASE_URL/openapi.json"; do
  if curl -sk "$endpoint" | tee "$SWAGGER_PATH" | grep -qi 'openapi\|swagger'; then
    break
  fi
done

python3 - <<PY
import json
from pathlib import Path
raw = Path(${RAW_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
swagger = Path(${SWAGGER_PATH@Q}).read_text(encoding='utf-8', errors='ignore') if Path(${SWAGGER_PATH@Q}).exists() else ''
findings = []
if 'x-powered-by: express' in raw.lower() or 'nestjs' in raw.lower():
    findings.append({'type': 'framework', 'value': 'NestJS/Express indicators observed'})
if '/swagger' in raw.lower() or '/swagger-json' in raw.lower() or 'swagger-ui' in raw.lower():
    findings.append({'type': 'docs', 'value': 'Swagger/OpenAPI route indicators observed'})
if swagger and ('openapi' in swagger.lower() or 'swagger' in swagger.lower()):
    findings.append({'type': 'openapi', 'value': 'OpenAPI/Swagger specification appears accessible'})
if 'access-control-allow-origin: *' in raw.lower():
    findings.append({'type': 'cors', 'value': 'Wildcard CORS observed'})
if 'validationpipe' in raw.lower() or 'class-validator' in raw.lower():
    findings.append({'type': 'framework-detail', 'value': 'Validation/class-transformer indicators observed'})
payload = {
    'target': ${TARGET@Q},
    'phase': 'enum',
    'script': 'scripts/enum/web/enum_nestjs_api.sh',
    'status': 'success',
    'safe_mode': bool(${SAFE_MODE}),
    'findings': findings,
    'artifacts': {
        'raw': ${RAW_PATH@Q},
        'parsed': ${PARSED_PATH@Q},
        'summary': ${SUMMARY_PATH@Q},
        'openapi': ${SWAGGER_PATH@Q},
    }
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [
    f"# NestJS API Enum — ${TARGET}",
    '',
    '- Engagement: ${ENGAGEMENT}',
    f'- Base URL: ${BASE_URL}',
    f'- Safe mode: ${SAFE_MODE}',
    f'- Findings: {len(findings)}',
    '',
    '## Findings',
]
summary.extend([f"- {item['type']}: {item['value']}" for item in findings] or ['- No notable NestJS/API findings captured'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
