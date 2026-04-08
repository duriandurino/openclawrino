#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: web_baseline.sh --target <host-or-url> --engagement <name> [--base-dir <path>] [--safe]
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
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "vuln", "web-baseline", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
HEADERS_PATH="${RAW_PATH%.txt}-headers.txt"
BODY_PATH="${RAW_PATH%.txt}-body.txt"
TRACE_PATH="${RAW_PATH%.txt}-trace.txt"

curl -skIL "$URL" > "$HEADERS_PATH" || true
curl -skL "$URL" | head -c 4000 > "$BODY_PATH" || true
if [[ "$SAFE_MODE" -eq 0 ]]; then
  curl -sk -X OPTIONS -i "$URL" > "$TRACE_PATH" || true
else
  printf 'safe mode enabled; skipped OPTIONS probe\n' > "$TRACE_PATH"
fi
cat "$HEADERS_PATH" "$BODY_PATH" "$TRACE_PATH" > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
headers = Path(${HEADERS_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
body = Path(${BODY_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
trace = Path(${TRACE_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
headers_lower = headers.lower()
findings = []
expected = {
    'content-security-policy': 'missing CSP header',
    'x-frame-options': 'missing X-Frame-Options header',
    'x-content-type-options': 'missing X-Content-Type-Options header',
    'strict-transport-security': 'missing HSTS header',
}
for header, desc in expected.items():
    if header not in headers_lower:
        findings.append({'type': 'header', 'candidate': desc, 'confidence': 'candidate'})
if 'index of /' in body.lower():
    findings.append({'type': 'content', 'candidate': 'possible directory listing exposed', 'confidence': 'candidate'})
if 'server:' in headers_lower:
    findings.append({'type': 'banner', 'candidate': 'server banner exposed', 'confidence': 'observed'})
if 'allow:' in trace.lower() and any(method in trace for method in ['PUT', 'DELETE', 'TRACE']):
    findings.append({'type': 'methods', 'candidate': 'potentially risky HTTP methods enabled', 'confidence': 'candidate'})
payload = {
    'target': ${TARGET@Q},
    'phase': 'vuln',
    'script': 'scripts/vuln/web/web_baseline.sh',
    'status': 'success',
    'safe_mode': bool(${SAFE_MODE}),
    'findings': findings,
    'artifacts': {
        'raw': ${RAW_PATH@Q},
        'parsed': ${PARSED_PATH@Q},
        'summary': ${SUMMARY_PATH@Q},
        'headers': ${HEADERS_PATH@Q},
        'body': ${BODY_PATH@Q},
        'options': ${TRACE_PATH@Q},
    }
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [
    f"# Web Baseline — ${TARGET}",
    "",
    "- Engagement: ${ENGAGEMENT}",
    "- URL: ${URL}",
    "- Safe mode: ${SAFE_MODE}",
    f"- Candidate findings: {len(findings)}",
    "",
    "## Findings",
]
summary.extend([f"- [{item['confidence']}] {item['candidate']}" for item in findings] or ["- No candidate findings captured"])
summary.append("")
summary.append("## Notes")
summary.append("- These are baseline observations only and require manual validation before reporting as findings.")
Path(${SUMMARY_PATH@Q}).write_text("\n".join(summary) + "\n", encoding='utf-8')
PY

echo "$SUMMARY_PATH"
