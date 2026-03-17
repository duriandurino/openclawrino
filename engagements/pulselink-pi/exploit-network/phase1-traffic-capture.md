# Phase 1: Traffic Capture (Recon Confirmation)

**Objective:** Capture MQTT traffic on the network to confirm device communication patterns and identify MQTT broker connections.

## Prerequisites

- Kali Linux with `tcpdump` installed (default)
- Network interface connected to same subnet as target (wlan0 or eth0)
- Root/sudo access for packet capture

## Step 1: Live Capture — Observe MQTT Traffic

```bash
# Capture MQTT traffic on port 8883 (MQTTS)
sudo tcpdump -i wlan0 -n port 8883 -c 100 -v
```

**What to look for:**
- TLS handshake (ClientHello, ServerHello, Certificate, etc.)
- After TLS negotiation, MQTT CONNECT packets (payload encrypted, but packet types visible)
- PINGREQ/PINGRESP heartbeat packets every ~30 seconds
- Source IP should be the Raspberry Pi (192.168.0.125)
- Destination should resolve to `pulse.n-compass.online`

## Step 2: Save Capture to File for Analysis

```bash
# Save full capture to pcap file
sudo tcpdump -i wlan0 -n port 8883 -w mqtt_capture.pcap -c 500
```

## Step 3: Quick Analysis of Saved Capture

```bash
# Read back the pcap and print ASCII payloads
sudo tcpdump -r mqtt_capture.pcap -A 2>/dev/null | head -50

# Filter for just the MQTT protocol (if tshark is available)
tshark -r mqtt_capture.pcap -Y "mqtt" -V 2>/dev/null | head -80
```

## Step 4: Identify Connection Details

```bash
# Extract unique source IPs connecting to port 8883
sudo tcpdump -r mqtt_capture.pcap -n 2>/dev/null | grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u

# Count packets per source IP
sudo tcpdump -r mqtt_capture.pcap -n 2>/dev/null | \
  grep -oP '\d+\.\d+\.\d+\.\d+' | sort | uniq -c | sort -rn
```

## What You Should See

### TLS Handshake Pattern
```
[IP].8883 > [Pi_IP].XXXXX: Flags [P.], ... length ...
  TLSv1.2 Record Layer: Handshake Protocol: Client Hello
    ...
    Extensions: server_name (type=0x0000), ... 
      Type: server_name (0)
      Server Name: pulse.n-compass.online
```

### MQTT Packet Types (visible through tshark even with TLS)
| Packet Type | Value | Meaning |
|-------------|-------|---------|
| CONNECT     | 1     | Client connecting to broker |
| CONNACK     | 2     | Broker acceptance |
| PUBLISH     | 3     | Message publish |
| PUBACK      | 4     | Publish acknowledgment |
| PINGREQ     | 12    | Keep-alive ping request |
| PINGRESP    | 13    | Keep-alive ping response |
| DISCONNECT  | 14    | Client disconnecting |

### Traffic Pattern Indicators

1. **Connection establishment:** ClientHello → ServerHello → Certificate → ChangeCipherSpec → CONNECT
2. **Keep-alive:** PINGREQ/PINGRESP every 30 seconds (default MQTT keep-alive)
3. **Publish patterns:** Bursts of PUBLISH packets when content updates occur
4. **Client identification:** MQTT CONNECT packet contains Client ID `dadf6f9ef35e55ab` (visible in cleartext within TLS if using tshark with keylogging, but header fields visible regardless)

## Key Observations for Next Phase

- Traffic flows to `pulse.n-compass.online:8883` → confirms MQTTS broker
- TLS 1.2/1.3 in use → need client certificates for MITM or replay
- Regular heartbeat pattern → device is actively connected
- If we can extract client certs (Phase 2), we can replay this connection

## Notes

- With TLS, actual MQTT payloads (topic names, messages) are encrypted at the transport layer
- The MQTT fixed header (packet type, flags) is visible in the TLS record but not directly readable without decryption
- Phase 2 extraction of client certificates will allow us to make our own authenticated connection
