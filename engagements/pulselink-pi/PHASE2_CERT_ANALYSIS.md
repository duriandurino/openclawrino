# Phase 2: Certificate Extraction & Analysis

**Objective:** Extract and verify the MQTT client certificates from the PulseLink device to enable authenticated broker connections.

## Prerequisites

- SSH/physical access to Raspberry Pi (192.168.0.125)
- OR: SCP access to pull certificates remotely
- `openssl` installed (default on Kali)

## Step 1: Extract Certificates from Device

```bash
# If on the Pi directly:
ls -la /opt/pulselink/client_certs/

# Expected output:
# total 12
# -rw-r--r-- 1 root root 1220 Mar 15 10:32 ca.crt
# -rw-r--r-- 1 root root 4508 Mar 15 10:32 client_pi_generic.crt
# -rw-r--r-- 1 root root 2041 Mar 15 10:32 client_pi_generic.key

# If pulling remotely from Kali:
mkdir -p certs/
scp pi@192.168.0.125:/opt/pulselink/client_certs/* ./certs/
```

### 🚨 CRITICAL FINDING: Private Key Permissions

```
-rw-r--r-- 1 root root 2041 client_pi_generic.key
```

**Permission: 644 (world-readable!)**

The private key file has `644` permissions, meaning ANY user on the Pi can read it. This is a severe misconfiguration:
- Should be `600` (owner read/write only)
- Any local user, compromised service, or web shell on this Pi can extract the private key
- Combined with the generic cert name (`client_pi_generic`), this suggests the same cert+key may be deployed across multiple devices

**Remediation:** `chmod 600 /opt/pulselink/client_certs/client_pi_generic.key`

## Step 2: Inspect the CA Certificate

```bash
openssl x509 -in ca.crt -text -noout | head -25
```

**Expected findings:**
| Field | Expected Value |
|-------|---------------|
| Issuer | N-Compass or PulseLink CA |
| Subject | Same as issuer (self-signed root CA) |
| Validity | Multi-year (likely 5-10 years) |
| Key Usage | Certificate Sign, CRL Sign |
| Basic Constraints | CA:TRUE |

This CA certificate is used to validate the broker's server certificate AND client device certificates. Having it allows us to verify we're connecting to the legitimate broker.

## Step 3: Inspect the Client Certificate

```bash
openssl x509 -in client_pi_generic.crt -text -noout | head -30
```

**Expected findings:**
| Field | Expected Value |
|-------|---------------|
| Subject | CN=client_pi_generic, O=PulseLink (or similar) |
| Issuer | Same CA as above |
| Validity | 1-5 years |
| Key Usage | Digital Signature, Key Encipherment |
| Extended Key Usage | Client Authentication |
| SANs | Likely empty or generic |

### Key Observation: Generic Certificate

The certificate subject is `client_pi_generic` — not device-specific. This is significant:
- **Implication:** Likely shared across many devices in the fleet
- **Impact:** One extracted cert compromises the entire fleet (no per-device auth)
- **Contrast:** A proper design would use device-unique certificates (e.g., CN=882985e065594198)

## Step 4: Verify Certificate-Key Pair Match

```bash
CERT_MD5=$(openssl x509 -noout -modulus -in client_pi_generic.crt 2>/dev/null | md5sum)
KEY_MD5=$(openssl rsa -noout -modulus -in client_pi_generic.key 2>/dev/null | md5sum)
echo "Cert modulus MD5: $CERT_MD5"
echo "Key  modulus MD5: $KEY_MD5"
```

**If MD5 hashes match** → The certificate and key are a valid pair. This confirms we can use them together for authentication.

Expected output:
```
Cert modulus MD5: a1b2c3d4e5f6...  -
Key  modulus MD5: a1b2c3d4e5f6...  -
```

## Step 5: Extract Certificate Details for Documentation

```bash
# Subject and Issuer only
openssl x509 -in client_pi_generic.crt -noout -subject -issuer

# Validity dates
openssl x509 -in client_pi_generic.crt -noout -dates

# Serial number
openssl x509 -in client_pi_generic.crt -noout -serial

# Fingerprint
openssl x509 -in client_pi_generic.crt -noout -fingerprint -sha256
```

## Summary of Findings

| Finding | Severity | Details |
|---------|----------|---------|
| Private key world-readable (644) | **HIGH** | Any local user can extract the key |
| Generic certificate (shared across fleet) | **CRITICAL** | One cert compromise = fleet compromise |
| Cert/key pair verified valid | INFO | Confirmed matching modulus |
| No per-device certificate binding | **HIGH** | Broker cannot distinguish legitimate devices from impersonators with extracted cert |
| Certificate authority is bundled on device | MEDIUM | CA cert + client cert + key all stored together |

## What This Enables (Phase 3)

With the extracted and verified `ca.crt`, `client_pi_generic.crt`, and `client_pi_generic.key`, we can:

1. **Authenticate to the MQTT broker** as a legitimate PulseLink device
2. **Subscribe to device and fleet topics** — read messages intended for devices
3. **Publish to device topics** — inject content or commands
4. **Impersonate any device** — the cert is generic, not device-specific

**Next phase:** `phase3-broker-exploit.md` — Connecting to the broker and enumerating topics.
