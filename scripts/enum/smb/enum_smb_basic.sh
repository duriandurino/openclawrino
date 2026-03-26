#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: enum_smb_basic.sh --target <host> --engagement <name> [--base-dir <path>] [--safe]
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
command -v smbclient >/dev/null 2>&1 || { echo "missing dependency: smbclient" >&2; exit 3; }
command -v enum4linux-ng >/dev/null 2>&1 || { echo "missing dependency: enum4linux-ng" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "smb-basic", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
SMBCLIENT_PATH="${RAW_PATH%.txt}-shares.txt"
ENUM4_PATH="${RAW_PATH%.txt}-enum4linux.txt"

{
  echo "# smbclient -L"
  smbclient -L "//$TARGET" -N || true
} > "$SMBCLIENT_PATH"

if [[ "$SAFE_MODE" -eq 0 ]]; then
  enum4linux-ng -A "$TARGET" > "$ENUM4_PATH" 2>&1 || true
else
  printf 'safe mode enabled; skipped enum4linux-ng -A\n' > "$ENUM4_PATH"
fi

cat "$SMBCLIENT_PATH" "$ENUM4_PATH" > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
shares_text = Path(${SMBCLIENT_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
enum_text = Path(${ENUM4_PATH@Q}).read_text(encoding='utf-8', errors='ignore')
findings = []
for line in shares_text.splitlines():
    stripped = line.strip()
    if stripped and not stripped.startswith(('Sharename', '---------', 'Anonymous login')) and 'Disk' in stripped:
        findings.append({"type": "share", "value": stripped})
if 'Domain Name:' in enum_text:
    for line in enum_text.splitlines():
        if 'Domain Name:' in line or 'NetBIOS computer name:' in line or 'OS:' in line:
            findings.append({"type": "enum", "value": line.strip()})
payload = {
    "target": ${TARGET@Q},
    "phase": "enum",
    "script": "scripts/enum/smb/enum_smb_basic.sh",
    "status": "success",
    "safe_mode": bool(${SAFE_MODE}),
    "findings": findings,
    "artifacts": {
        "raw": ${RAW_PATH@Q},
        "parsed": ${PARSED_PATH@Q},
        "summary": ${SUMMARY_PATH@Q},
        "smbclient": ${SMBCLIENT_PATH@Q},
        "enum4linux": ${ENUM4_PATH@Q},
    }
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [
    f"# SMB Basic Enum — ${TARGET}",
    "",
    "- Engagement: ${ENGAGEMENT}",
    "- Safe mode: ${SAFE_MODE}",
    f"- Findings: {len(findings)}",
    "",
    "## Highlights",
]
summary.extend([f"- {item['value']}" for item in findings[:20]] or ["- No notable SMB findings captured"])
summary.append("")
summary.append("## Artifacts")
summary.append("- Raw: ${RAW_PATH}")
summary.append("- Parsed: ${PARSED_PATH}")
summary.append("- Summary: ${SUMMARY_PATH}")
Path(${SUMMARY_PATH@Q}).write_text("\n".join(summary) + "\n", encoding='utf-8')
PY

echo "$SUMMARY_PATH"
