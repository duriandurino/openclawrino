#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: enum_graphql_basic.sh --target <host-or-url> --engagement <name> [--base-dir <path>] [--safe]
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
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "graphql-basic", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
INTROSPECTION_PATH="${RAW_PATH%.txt}-introspection.json"
ENDPOINTS_PATH="${RAW_PATH%.txt}-endpoints.txt"

ENDPOINTS=("$BASE_URL/graphql" "$BASE_URL/api/graphql" "$BASE_URL/query" "$BASE_URL/graphiql")
printf '%s\n' "${ENDPOINTS[@]}" > "$ENDPOINTS_PATH"
INTROSPECTION_QUERY='{"query":"query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { name kind } } }"}'

{
  echo "# GraphQL endpoint probe"
  for endpoint in "${ENDPOINTS[@]}"; do
    echo "## $endpoint"
    curl -sk -i -X POST "$endpoint" -H 'Content-Type: application/json' --data "$INTROSPECTION_QUERY" || true
    echo
  done
} > "$RAW_PATH"

FOUND_ENDPOINT=""
if [[ "$SAFE_MODE" -eq 1 ]]; then
  for endpoint in "${ENDPOINTS[@]}"; do
    if curl -sk -X POST "$endpoint" -H 'Content-Type: application/json' --data "$INTROSPECTION_QUERY" | grep -q '__schema'; then
      FOUND_ENDPOINT="$endpoint"
      curl -sk -X POST "$endpoint" -H 'Content-Type: application/json' --data "$INTROSPECTION_QUERY" > "$INTROSPECTION_PATH" || true
      break
    fi
  done
else
  for endpoint in "${ENDPOINTS[@]}"; do
    if curl -sk -X POST "$endpoint" -H 'Content-Type: application/json' --data "$INTROSPECTION_QUERY" | tee "$INTROSPECTION_PATH" | grep -q '__schema'; then
      FOUND_ENDPOINT="$endpoint"
      break
    fi
  done
fi

python3 - <<PY
import json
from pathlib import Path
raw = Path(${RAW_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
introspection = Path(${INTROSPECTION_PATH@Q}).read_text(encoding='utf-8', errors='ignore') if Path(${INTROSPECTION_PATH@Q}).exists() else ''
findings = []
for endpoint in Path(${ENDPOINTS_PATH@Q}).read_text(encoding='utf-8', errors='ignore').splitlines():
    if endpoint and endpoint in raw:
        findings.append({'type': 'endpoint-probe', 'value': endpoint})
if ${FOUND_ENDPOINT@Q}:
    findings.append({'type': 'graphql-endpoint', 'value': ${FOUND_ENDPOINT@Q}})
if '__schema' in introspection:
    findings.append({'type': 'introspection', 'value': 'GraphQL introspection appears enabled'})
if 'graphiql' in raw.lower() or 'apollo sandbox' in raw.lower():
    findings.append({'type': 'graphql-ui', 'value': 'GraphQL interactive UI indicators observed'})
payload = {
    'target': ${TARGET@Q},
    'phase': 'enum',
    'script': 'scripts/enum/web/enum_graphql_basic.sh',
    'status': 'success',
    'safe_mode': bool(${SAFE_MODE}),
    'findings': findings,
    'artifacts': {
        'raw': ${RAW_PATH@Q},
        'parsed': ${PARSED_PATH@Q},
        'summary': ${SUMMARY_PATH@Q},
        'introspection': ${INTROSPECTION_PATH@Q},
    }
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [
    f"# GraphQL Basic Enum — ${TARGET}",
    '',
    '- Engagement: ${ENGAGEMENT}',
    f'- Base URL: ${BASE_URL}',
    f'- Safe mode: ${SAFE_MODE}',
    f'- Findings: {len(findings)}',
    '',
    '## Findings',
]
summary.extend([f"- {item['type']}: {item['value']}" for item in findings] or ['- No notable GraphQL findings captured'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
