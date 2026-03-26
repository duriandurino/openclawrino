#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: api_auth_probe.sh --target <host-or-url> --engagement <name> [--base-dir <path>] [--safe]
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
  URL="$TARGET"
else
  URL="http://$TARGET"
fi

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "recon", "api-auth-probe", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
DOCS_PATH="${RAW_PATH%.txt}-docs.txt"
OPTIONS_PATH="${RAW_PATH%.txt}-options.txt"
AUTH_PATH="${RAW_PATH%.txt}-auth.txt"

{
  echo "# docs endpoints"
  for path in /swagger /swagger.json /openapi.json /docs /api/docs; do
    code=$(curl -sk -o /dev/null -w '%{http_code}' "$URL$path" || true)
    echo "$path $code"
  done
} > "$DOCS_PATH"

if [[ "$SAFE_MODE" -eq 0 ]]; then
  curl -sk -X OPTIONS -i "$URL" > "$OPTIONS_PATH" || true
else
  printf 'safe mode enabled; skipped OPTIONS probe\n' > "$OPTIONS_PATH"
fi

{
  echo "# unauthenticated auth-ish endpoints"
  for path in /login /auth/login /api/login /api/me /me /profile; do
    code=$(curl -sk -o /dev/null -w '%{http_code}' "$URL$path" || true)
    echo "$path $code"
  done
} > "$AUTH_PATH"

cat "$DOCS_PATH" "$OPTIONS_PATH" "$AUTH_PATH" > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
docs = Path(${DOCS_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
options = Path(${OPTIONS_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
auth = Path(${AUTH_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
findings = []
for line in docs.splitlines():
    parts = line.strip().split()
    if len(parts) == 2 and parts[1].isdigit() and parts[1] not in ('000', '404'):
        findings.append({'type': 'api-docs', 'value': f'{parts[0]} returned {parts[1]}', 'confidence': 'observed'})
for line in auth.splitlines():
    parts = line.strip().split()
    if len(parts) == 2 and parts[1] in ('200', '204', '302', '401', '403'):
        findings.append({'type': 'api-auth', 'value': f'{parts[0]} returned {parts[1]}', 'confidence': 'candidate'})
if 'allow:' in options.lower():
    allow_line = next((ln.strip() for ln in options.splitlines() if ln.lower().startswith('allow:')), '')
    if allow_line:
        findings.append({'type': 'api-methods', 'value': allow_line, 'confidence': 'observed'})
payload = {
  'target': ${TARGET@Q},
  'phase': 'recon',
  'script': 'scripts/recon/web/api_auth_probe.sh',
  'status': 'success',
  'safe_mode': bool(${SAFE_MODE}),
  'findings': findings,
  'artifacts': {'raw': ${RAW_PATH@Q}, 'parsed': ${PARSED_PATH@Q}, 'summary': ${SUMMARY_PATH@Q}, 'docs': ${DOCS_PATH@Q}, 'options': ${OPTIONS_PATH@Q}, 'auth': ${AUTH_PATH@Q}}
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [f"# API Auth Probe — ${TARGET}", '', f"- Engagement: ${ENGAGEMENT}", f"- Safe mode: ${SAFE_MODE}", f"- Findings: {len(findings)}", '', '## Highlights']
summary.extend([f"- {item['value']}" for item in findings[:20]] or ['- No notable API/auth findings captured'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
