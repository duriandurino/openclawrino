# Network Traffic Capture Guide
## PulseLink Pi — MQTT Traffic Analysis

**Target:** 192.168.0.125 (Raspberry Pi 5)
**Broker:** pulse.n-compass.online:8883 (TLS)
**Date:** 2026-03-17

---

## 1. Prerequisites

```bash
# Verify tcpdump is installed
which tcpdump || sudo apt install tcpdump -y

# Identify your network interface
ip addr show
# Look for wlan0 (WiFi) or eth0 (Ethernet)

# Check if you can reach the Pi
ping -c 3 192.168.0.125
```

## 2. Discover MQTT Traffic on the Network

### Quick live capture (100 packets, verbose)
```bash
sudo tcpdump -i wlan0 -n port 8883 -c 100 -v
```

### If WiFi interface differs, use this to find it
```bash
# List all interfaces
ip -brief link show

# Then replace wlan0 with your interface
sudo tcpdump -i eth0 -n port 8883 -c 100 -v
```

## 3. Capture MQTT Traffic to File

### Full capture for offline analysis (500 packets)
```bash
sudo tcpdump -i wlan0 -n port 8883 -w /tmp/mqtt_capture.pcap -c 500
```

### Extended capture with ring buffer (keeps last 10 files of 10MB each)
```bash
sudo tcpdump -i wlan0 -n port 8883 \
  -w /tmp/mqtt_capture.pcap \
  -C 10 \
  -W 10 \
  -c 5000
```

### Capture ALL traffic to/from the Pi (not just MQTT)
```bash
sudo tcpdump -i wlan0 -n host 192.168.0.125 \
  -w /tmp/pi_all_traffic.pcap \
  -c 1000
```

### Capture with timestamps (microsecond precision)
```bash
sudo tcpdump -i wlan0 -n port 8883 \
  --time-stamp-precision micro \
  -w /tmp/mqtt_ts_capture.pcap \
  -c 500
```

## 4. Analyze Captured Traffic

### ASCII dump of captured packets
```bash
sudo tcpdump -r /tmp/mqtt_capture.pcap -A | head -100
```

### Hex + ASCII dump (good for binary protocol analysis)
```bash
sudo tcpdump -r /tmp/mqtt_capture.pcap -X | head -100
```

### Look for MQTT control packet types
MQTT packet types in first nibble:
- `10` = CONNECT
- `20` = CONNACK
- `30` = PUBLISH
- `40` = PUBACK
- `50` = PUBREC
- `80` = SUBSCRIBE
- `90` = SUBACK
- `C0` = PINGREQ
- `D0` = PINGRESP

```bash
sudo tcpdump -r /tmp/mqtt_capture.pcap -X | grep -E "10 |20 |30 |40 |50 |80 |90 |c0 |d0 " | head -20
```

### Extract string data (topics, client IDs)
```bash
sudo tcpdump -r /tmp/mqtt_capture.pcap -A | grep -E "(device|status|command|content|heartbeat|fleet)" | head -30
```

### Show packet summaries only
```bash
sudo tcpdump -r /tmp/mqtt_capture.pcap -n
```

## 5. Advanced Capture Filters

### Capture only MQTT CONNECT packets
```bash
sudo tcpdump -i wlan0 -n "tcp port 8883 and tcp[((tcp[12:1] & 0xf0) >> 2):1] = 0x10" \
  -w /tmp/mqtt_connect.pcap -c 50
```

### Capture only PUBLISH packets
```bash
sudo tcpdump -i wlan0 -n "tcp port 8883 and tcp[((tcp[12:1] & 0xf0) >> 2):1] = 0x30" \
  -w /tmp/mqtt_publish.pcap -c 100
```

### Capture MQTT + DNS (to see resolution of pulse.n-compass.online)
```bash
sudo tcpdump -i wlan0 -n "port 8883 or port 53" \
  -w /tmp/mqtt_dns.pcap -c 200
```

## 6. Using Wireshark (GUI Analysis)

If you have a display available:
```bash
# Install Wireshark if needed
sudo apt install wireshark -y

# Open capture file in Wireshark
wireshark /tmp/mqtt_capture.pcap &
```

Wireshark has native MQTT protocol dissection — it will decode CONNECT, PUBLISH, SUBSCRIBE packets automatically. Filter with: `mqtt`

## 7. Using tshark (CLI Wireshark)

```bash
# Install tshark
sudo apt install tshark -y

# Extract MQTT fields from capture
tshark -r /tmp/mqtt_capture.pcap -Y mqtt -T fields \
  -e frame.time -e mqtt.type -e mqtt.topic -e mqtt.msg

# Count MQTT packet types
tshark -r /tmp/mqtt_capture.pcap -Y mqtt -T fields -e mqtt.type | sort | uniq -c | sort -rn
```

## 8. Real-time MQTT Monitoring

### Watch for new connections in real-time
```bash
# In one terminal: capture
sudo tcpdump -i wlan0 -n port 8883 -l | grep --line-buffered -E "CONNECT|PUBLISH|SUBSCRIBE"
```

### Continuous capture with rolling files
```bash
sudo tcpdump -i wlan0 -n port 8883 \
  -w /tmp/mqtt_live.pcap \
  -C 50 \
  -W 5 \
  -U  # Unbuffered for real-time writing
```

## 9. Important Notes

- **Port 8883 = MQTT over TLS** — payload will be encrypted
- You will see TCP handshake, TLS handshake, but NOT plaintext MQTT messages
- To decrypt TLS, you need the private key — see `tls-analysis.md`
- Focus on **metadata**: connection patterns, timing, packet sizes, frequency
- The Pi itself may be sniffing on promiscuous mode — be aware of detection

## 10. What to Look For

| What | Why | How |
|------|-----|-----|
| Connection frequency | How often Pi phones home | Timestamps between CONNECT packets |
| Packet sizes | Content updates vs heartbeats | PUBLISH packet lengths |
| TLS handshake details | Cipher suites, cert info | `openssl s_client` |
| DNS queries | Domain resolution patterns | Capture port 53 alongside 8883 |
| Source port patterns | Identify specific clients | Track ports across sessions |
