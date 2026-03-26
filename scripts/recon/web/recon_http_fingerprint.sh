#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: recon_http_fingerprint.sh --target <host-or-url> --engagement <name> [--base-dir <path>]
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
command -v curl >/dev/null 2>&1 || { echo "missing dependency: curl" >&2; exit 3; }
command -v whatweb >/dev/null 2>&1 || { echo "missing dependency: whatweb" >&2; exit 3; }
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
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "recon", "recon-http-fingerprint", ${TARGET@Q})
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
WHATWEB_PATH="${RAW_PATH%.txt}-whatweb.txt"

curl -skI "$URL" > "$HEADERS_PATH" || true
curl -skL "$URL" | head -c 3000 > "$BODY_PATH" || true
whatweb "$URL" > "$WHATWEB_PATH" 2>/dev/null || true
cat "$HEADERS_PATH" "$BODY_PATH" "$WHATWEB_PATH" > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
headers = Path(${HEADERS_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
body = Path(${BODY_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
whatweb = Path(${WHATWEB_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
findings = []
for line in headers.splitlines():
    if line.lower().startswith(('server:', 'x-powered-by:', 'location:')):
        findings.append({'type': 'header', 'value': line.strip()})
if '<title>' in body.lower():
    lower = body.lower()
    start = lower.find('<title>') + 7
    end = lower.find('</title>', start)
    if end > start:
        findings.append({'type': 'title', 'value': body[start:end].strip()})
if whatweb.strip():
    findings.append({'type': 'whatweb', 'value': whatweb.strip()})
payload = {
    'target': ${TARGET@Q},
    'phase': 'recon',
    'script': 'scripts/recon/web/recon_http_fingerprint.sh',
    'status': 'success',
    'findings': findings,
    'artifacts': {'raw': ${RAW_PATH@Q}, 'parsed': ${PARSED_PATH@Q}, 'summary': ${SUMMARY_PATH@Q}, 'headers': ${HEADERS_PATH@Q}, 'body': ${BODY_PATH@Q}, 'whatweb': ${WHATWEB_PATH@Q}}
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [f"# HTTP Fingerprint — ${TARGET}", '', f"- Engagement: ${ENGAGEMENT}", f"- URL: ${URL}", f"- Findings: {len(findings)}", '', '## Highlights']
summary.extend([f"- {item['type']}: {item['value']}" for item in findings[:20]] or ['- No notable fingerprint data captured'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
