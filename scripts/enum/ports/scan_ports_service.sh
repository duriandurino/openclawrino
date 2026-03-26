#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scan_ports_service.sh --target <host> --engagement <name> [--ports 80,443] [--base-dir <path>]
EOF
}

TARGET=""
ENGAGEMENT=""
PORTS=""
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --ports) PORTS="$2"; shift 2 ;;
    --base-dir) BASE_DIR="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

[[ -n "$TARGET" && -n "$ENGAGEMENT" ]] || { usage; exit 2; }
command -v nmap >/dev/null 2>&1 || { echo "missing dependency: nmap" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }

if [[ -z "$PORTS" ]]; then
  latest_json=$(find "$BASE_DIR/engagements/$ENGAGEMENT/enum/parsed" -maxdepth 1 -type f -name 'nmap-fast-*.json' 2>/dev/null | sort | tail -n1 || true)
  [[ -n "$latest_json" ]] || { echo "no fast-scan JSON found; provide --ports explicitly or run scan_ports_fast.sh first" >&2; exit 2; }
  PORTS=$(python3 - <<PY
import json
from pathlib import Path
payload = json.loads(Path(${latest_json@Q}).read_text())
ports = [str(item['port']) for item in payload.get('open_ports', [])]
print(','.join(ports))
PY
)
fi

if [[ -z "$PORTS" ]]; then
  mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "nmap-service", ${TARGET@Q}, raw_ext="gnmap")
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
  RAW_PATH="${PATHS[0]}"
  PARSED_PATH="${PATHS[1]}"
  SUMMARY_PATH="${PATHS[2]}"
  printf 'No ports provided or discovered for follow-up service scan.\n' > "$RAW_PATH"
  printf '{\n  "target": "%s",\n  "phase": "enum",\n  "script": "scripts/enum/ports/scan_ports_service.sh",\n  "status": "no-op",\n  "open_ports": []\n}\n' "$TARGET" > "$PARSED_PATH"
  cat > "$SUMMARY_PATH" <<EOF
# Service Scan — $TARGET

- Engagement: $ENGAGEMENT
- Target: $TARGET
- Status: no-op
- Reason: no ports provided or discovered from prior fast scan
EOF
  echo "$SUMMARY_PATH"
  exit 0
fi

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "nmap-service", ${TARGET@Q}, raw_ext="gnmap")
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
NORMAL_PATH="${RAW_PATH%.gnmap}.txt"
XML_PATH="${RAW_PATH%.gnmap}.xml"

nmap -Pn -sV -sC -p "$PORTS" -oG "$RAW_PATH" -oN "$NORMAL_PATH" -oX "$XML_PATH" "$TARGET"
python3 "$BASE_DIR/scripts/shared/parsers/nmap_to_json.py" --input "$RAW_PATH" --output "$PARSED_PATH" >/dev/null

python3 - <<PY
import json
from pathlib import Path
parsed = json.loads(Path(${PARSED_PATH@Q}).read_text())
ports = parsed.get("open_ports", [])
summary = [
    f"# Service Scan — ${TARGET}",
    "",
    "- Engagement: ${ENGAGEMENT}",
    "- Target: ${TARGET}",
    "- Ports scanned: ${PORTS}",
    f"- Open ports confirmed: {len(ports)}",
    "",
    "## Open ports",
]
if ports:
    summary.extend([f"- {p['port']}/{p['protocol']} — {p['service']}" for p in ports])
else:
    summary.append("- No open ports confirmed during service scan")
summary.append("")
summary.append("## Artifacts")
summary.append("- Raw: ${RAW_PATH}")
summary.append("- Parsed: ${PARSED_PATH}")
summary.append("- Summary: ${SUMMARY_PATH}")
Path(${SUMMARY_PATH@Q}).write_text("\n".join(summary) + "\n", encoding="utf-8")
PY

echo "$SUMMARY_PATH"
