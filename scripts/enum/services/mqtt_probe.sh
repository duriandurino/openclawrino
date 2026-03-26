#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: mqtt_probe.sh --target <host> --engagement <name> [--base-dir <path>] [--safe]
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
command -v nc >/dev/null 2>&1 || { echo "missing dependency: nc" >&2; exit 3; }
command -v timeout >/dev/null 2>&1 || { echo "missing dependency: timeout" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "missing dependency: python3" >&2; exit 3; }

mapfile -t PATHS < <(python3 - <<PY
import sys
from pathlib import Path
root = Path(${BASE_DIR@Q})
sys.path.insert(0, str(root))
from scripts.shared.lib.output_helpers import artifact_paths
paths = artifact_paths(root, ${ENGAGEMENT@Q}, "enum", "mqtt-probe", ${TARGET@Q})
print(paths["raw"])
print(paths["parsed"])
print(paths["summary"])
PY
)
RAW_PATH="${PATHS[0]}"
PARSED_PATH="${PATHS[1]}"
SUMMARY_PATH="${PATHS[2]}"
MQTT1883_PATH="${RAW_PATH%.txt}-1883.txt"
MQTT8883_PATH="${RAW_PATH%.txt}-8883.txt"

probe_port() {
  local port="$1"
  local out="$2"
  if timeout 5 bash -lc "printf '' | nc -v -w 3 '$TARGET' '$port'" >"$out" 2>&1; then
    return 0
  fi
  return 1
}

probe_port 1883 "$MQTT1883_PATH" || true
probe_port 8883 "$MQTT8883_PATH" || true
cat "$MQTT1883_PATH" "$MQTT8883_PATH" > "$RAW_PATH"

python3 - <<PY
import json
from pathlib import Path
p1883 = Path(${MQTT1883_PATH@Q}).read_text(encoding='utf-8', errors='ignore') if Path(${MQTT1883_PATH@Q}).exists() else ''
p8883 = Path(${MQTT8883_PATH@Q}).read_text(encoding='utf-8', errors='ignore') if Path(${MQTT8883_PATH@Q}).exists() else ''
findings = []
for port, text in [('1883', p1883), ('8883', p8883)]:
    lower = text.lower()
    if 'succeeded' in lower or 'open' in lower or 'connected' in lower:
        findings.append({'type': 'mqtt-port', 'value': f'{port}/tcp reachable', 'confidence': 'observed'})
    elif 'refused' in lower:
        findings.append({'type': 'mqtt-port', 'value': f'{port}/tcp refused', 'confidence': 'observed-defensive'})
    elif 'timed out' in lower:
        findings.append({'type': 'mqtt-port', 'value': f'{port}/tcp timed out', 'confidence': 'observed'})
    if 'ssl' in lower or 'tls' in lower:
        findings.append({'type': 'mqtt-tls', 'value': f'{port}/tcp appears TLS-related', 'confidence': 'candidate'})
payload = {
  'target': ${TARGET@Q},
  'phase': 'enum',
  'script': 'scripts/enum/services/mqtt_probe.sh',
  'status': 'success',
  'safe_mode': bool(${SAFE_MODE}),
  'findings': findings,
  'artifacts': {
    'raw': ${RAW_PATH@Q},
    'parsed': ${PARSED_PATH@Q},
    'summary': ${SUMMARY_PATH@Q},
    'mqtt1883': ${MQTT1883_PATH@Q},
    'mqtt8883': ${MQTT8883_PATH@Q},
  }
}
Path(${PARSED_PATH@Q}).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
summary = [f"# MQTT Probe — ${TARGET}", '', f"- Engagement: ${ENGAGEMENT}", f"- Safe mode: ${SAFE_MODE}", f"- Findings: {len(findings)}", '', '## Highlights']
summary.extend([f"- {item['value']}" for item in findings[:20]] or ['- No MQTT-specific exposure observed on 1883/8883'])
Path(${SUMMARY_PATH@Q}).write_text('\n'.join(summary) + '\n', encoding='utf-8')
PY

echo "$SUMMARY_PATH"
