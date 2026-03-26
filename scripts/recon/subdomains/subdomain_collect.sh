#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: subdomain_collect.sh --domain <domain> --engagement <name> [--base-dir <path>]
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
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }
command -v subfinder >/dev/null 2>&1 || { echo "missing dependency: subfinder" >&2; exit 3; }
command -v amass >/dev/null 2>&1 || { echo "missing dependency: amass" >&2; exit 3; }
command -v curl >/dev/null 2>&1 || { echo "missing dependency: curl" >&2; exit 3; }

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "recon", "subdomain-collect", ${DOMAIN@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
SUBFINDER_PATH="${RAW_PATH%.txt}-subfinder.txt"
AMASS_PATH="${RAW_PATH%.txt}-amass.txt"
CRT_PATH="${RAW_PATH%.txt}-crtsh.txt"
MERGED_PATH="${RAW_PATH%.txt}-merged.txt"

subfinder -silent -d "$DOMAIN" > "$SUBFINDER_PATH" 2>/dev/null || true
amass enum -passive -d "$DOMAIN" > "$AMASS_PATH" 2>/dev/null || true
curl -s "https://crt.sh/?q=%.${DOMAIN}&output=json" | python3 - <<'PY' > "$CRT_PATH"
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    data = []
seen = set()
for entry in data:
    for name in entry.get('name_value', '').split('\n'):
        name = name.strip().lower()
        if name.startswith('*.'):
            name = name[2:]
        if name:
            seen.add(name)
for item in sorted(seen):
    print(item)
PY
cat "$SUBFINDER_PATH" "$AMASS_PATH" "$CRT_PATH" | sed '/^$/d' | sort -u > "$MERGED_PATH"
cat "$SUBFINDER_PATH" "$AMASS_PATH" "$CRT_PATH" > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
subs = [line.strip() for line in Path(${MERGED_PATH@Q}).read_text(encoding='utf-8', errors='ignore').splitlines() if line.strip()]
payload = {
    'target': ${DOMAIN@Q},
    'phase': 'recon',
    'script': 'scripts/recon/subdomains/subdomain_collect.sh',
    'status': 'success',
    'findings': [{'type': 'subdomain', 'value': item} for item in subs],
    'artifacts': {'raw': ${RAW_PATH@Q}, 'parsed': ${PARSED_PATH@Q}, 'summary': ${SUMMARY_PATH@Q}, 'merged': ${MERGED_PATH@Q}, 'subfinder': ${SUBFINDER_PATH@Q}, 'amass': ${AMASS_PATH@Q}, 'crtsh': ${CRT_PATH@Q}}
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [f"# Subdomain Collection — ${DOMAIN}", '', f"- Engagement: ${ENGAGEMENT}", f"- Unique subdomains: {len(subs)}", '', '## Highlights']
summary.extend([f"- {item}" for item in subs[:50]] or ['- No subdomains collected'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
