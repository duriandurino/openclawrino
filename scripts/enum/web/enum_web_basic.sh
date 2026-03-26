#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: enum_web_basic.sh --target <host-or-url> --engagement <name> [--base-dir <path>] [--safe]
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
command -v ffuf >/dev/null 2>&1 || { echo "missing dependency: ffuf" >&2; exit 3; }
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
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "web-basic", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
HEADERS_PATH="${RAW_PATH%.txt}-headers.txt"
ROBOTS_PATH="${RAW_PATH%.txt}-robots.txt"
FFUF_PATH="${RAW_PATH%.txt}-ffuf.json"

{
  echo "# curl -I"
  curl -skI "$URL" || true
  echo
  echo "# curl body preview"
  curl -skL "$URL" | head -c 2000 || true
} > "$RAW_PATH"

curl -skI "$URL" > "$HEADERS_PATH" || true
curl -skL "$URL/robots.txt" > "$ROBOTS_PATH" || true

if [[ "$SAFE_MODE" -eq 0 ]]; then
  ffuf -u "$URL/FUZZ" -w /usr/share/wordlists/dirb/common.txt -mc all -fc 404 -of json -o "$FFUF_PATH" >/dev/null 2>&1 || true
else
  echo '{"results":[]}' > "$FFUF_PATH"
fi

python3 - <<PY
import json
from pathlib import Path
headers = Path(${HEADERS_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
robots = Path(${ROBOTS_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
ffuf_data = json.loads(Path(${FFUF_PATH@Q}).read_text(encoding='utf-8', errors='ignore')) if Path(${FFUF_PATH@Q}).exists() else {"results": []}
results = []
for line in robots.splitlines():
    if line.lower().startswith(('allow:', 'disallow:')):
        results.append({"type": "robots", "value": line.strip()})
for item in ffuf_data.get('results', [])[:50]:
    results.append({
        "type": "path",
        "url": item.get('url'),
        "status": item.get('status'),
        "length": item.get('length'),
    })
payload = {
    "target": ${TARGET@Q},
    "phase": "enum",
    "script": "scripts/enum/web/enum_web_basic.sh",
    "status": "success",
    "safe_mode": bool(${SAFE_MODE}),
    "findings": results,
    "artifacts": {
        "raw": ${RAW_PATH@Q},
        "parsed": ${PARSED_PATH@Q},
        "summary": ${SUMMARY_PATH@Q},
        "headers": ${HEADERS_PATH@Q},
        "robots": ${ROBOTS_PATH@Q},
        "ffuf": ${FFUF_PATH@Q},
    }
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + "\n", encoding='utf-8')
summary = [
    f"# Web Basic Enum — ${TARGET}",
    "",
    "- Engagement: ${ENGAGEMENT}",
    "- URL: ${URL}",
    "- Safe mode: ${SAFE_MODE}",
    f"- Findings: {len(results)}",
    "",
    "## Highlights",
]
if results:
    for item in results[:20]:
        if item['type'] == 'robots':
            summary.append(f"- robots: {item['value']}")
        else:
            summary.append(f"- {item['status']} {item['url']} (len={item['length']})")
else:
    summary.append("- No notable web findings captured")
summary.append("")
summary.append("## Artifacts")
summary.append(f"- Raw: `{${RAW_PATH@Q}}`")
summary.append(f"- Parsed: `{${PARSED_PATH@Q}}`")
summary.append(f"- Summary: `{${SUMMARY_PATH@Q}}`")
Path(${SUMMARY_PATH@Q}).write_text("\n".join(summary) + "\n", encoding='utf-8')
PY

echo "$SUMMARY_PATH"
