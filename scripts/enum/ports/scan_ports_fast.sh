#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scan_ports_fast.sh --target <host> --engagement <name> [--base-dir <path>]
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
command -v nmap >/dev/null 2>&1 || { echo "missing dependency: nmap" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "nmap-fast", ${TARGET@Q}, raw_ext="gnmap")
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

nmap -Pn --top-ports 1000 -T4 -oG "$RAW_PATH" -oN "$NORMAL_PATH" -oX "$XML_PATH" "$TARGET"
python3 "$BASE_DIR/scripts/shared/parsers/nmap_to_json.py" --input "$RAW_PATH" --output "$PARSED_PATH" >/dev/null

python3 - <<PY
import json
from pathlib import Path
parsed = json.loads(Path(${PARSED_PATH@Q}).read_text())
ports = parsed.get("open_ports", [])
summary = [
    f"# Fast Port Scan — ${TARGET}",
    "",
    f"- Engagement: `${ENGAGEMENT}`",
    f"- Target: `${TARGET}`",
    f"- Open ports: {len(ports)}",
    "",
    "## Open ports",
]
if ports:
    summary.extend([f"- {p['port']}/{p['protocol']} — {p['service']}" for p in ports])
else:
    summary.append("- No open ports found in top 1000 scan")
summary.append("")
summary.append("## Artifacts")
summary.append(f"- Raw: `{${RAW_PATH@Q}}`")
summary.append(f"- Parsed: `{${PARSED_PATH@Q}}`")
summary.append(f"- Summary: `{${SUMMARY_PATH@Q}}`")
Path(${SUMMARY_PATH@Q}).write_text("\n".join(summary) + "\n", encoding="utf-8")
PY

echo "$SUMMARY_PATH"
