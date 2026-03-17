# TLS Certificate Analysis
## PulseLink Pi — MQTT TLS Inspection

**Target Broker:** pulse.n-compass.online:8883
**Client Certs Path:** /opt/pulselink/client_certs/
**Date:** 2026-03-17

---

## 1. Extract Certificates from Pi

```bash
# SSH into the Pi
ssh pi@192.168.0.125

# List certificate files
sudo ls -la /opt/pulselink/client_certs/
# Expected files:
#   ca.crt              — Certificate Authority
#   client_pi_generic.crt — Client certificate
#   client_pi_generic.key — Client private key

# Copy all certs to Kali
mkdir -p ~/pulselink-certs
scp pi@192.168.0.125:/opt/pulselink/client_certs/* ~/pulselink-certs/
chmod 600 ~/pulselink-certs/*.key
```

## 2. Certificate Authority Analysis

### View full CA certificate
```bash
openssl x509 -in ~/pulselink-certs/ca.crt -text -noout
```

### Extract key fields
```bash
# Subject and Issuer
openssl x509 -in ~/pulselink-certs/ca.crt -subject -issuer -noout

# Validity period
openssl x509 -in ~/pulselink-certs/ca.crt -dates -noout

# Serial number
openssl x509 -in ~/pulselink-certs/ca.crt -serial -noout

# Public key info
openssl x509 -in ~/pulselink-certs/ca.crt -pubkey -noout

# Fingerprints
openssl x509 -in ~/pulselink-certs/ca.crt -fingerprint -sha256 -noout
openssl x509 -in ~/pulselink-certs/ca.crt -fingerprint -md5 -noout

# Subject Alternative Names (if any)
openssl x509 -in ~/pulselink-certs/ca.crt -text -noout | grep -A1 "Subject Alternative"
```

### Check if CA is self-signed
```bash
openssl verify -CAfile ~/pulselink-certs/ca.crt ~/pulselink-certs/ca.crt
# Should return: ca.crt: OK (self-signed)
```

## 3. Client Certificate Analysis

### View full client certificate
```bash
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -text -noout
```

### Extract key fields
```bash
# Subject and Issuer
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -subject -issuer -noout

# Validity
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -dates -noout

# Is it expired?
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -checkend 0 -noout
echo $?
# 0 = valid, 1 = expired

# Check expiry in days
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -checkend 2592000 -noout
echo $?
# Will expire within 30 days?

# Serial number (compare across devices)
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -serial -noout

# SANs
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -text -noout | grep -A1 "Subject Alternative"

# Key usage
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -text -noout | grep -A1 "Key Usage"
```

### Verify client cert against CA
```bash
openssl verify -CAfile ~/pulselink-certs/ca.crt ~/pulselink-certs/client_pi_generic.crt
# Expected: client_pi_generic.crt: OK
```

## 4. Private Key Analysis

### View key details (DON'T display actual key material in notes)
```bash
# Key type and size
openssl rsa -in ~/pulselink-certs/client_pi_generic.key -text -noout 2>/dev/null | head -5
# OR for EC keys
openssl ec -in ~/pulselink-certs/client_pi_generic.key -text -noout 2>/dev/null | head -5

# Key check (validates integrity without exposing)
openssl rsa -in ~/pulselink-certs/client_pi_generic.key -check -noout 2>/dev/null
openssl ec -in ~/pulselink-certs/client_pi_generic.key -check -noout 2>/dev/null

# Key fingerprint
openssl pkey -in ~/pulselink-certs/client_pi_generic.key -pubout | \
  openssl dgst -sha256
```

### Check if key matches certificate
```bash
# Compare public key from cert vs public key from private key
cert_pubkey=$(openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -pubkey -noout)
key_pubkey=$(openssl pkey -in ~/pulselink-certs/client_pi_generic.key -pubout)
if [ "$cert_pubkey" = "$key_pubkey" ]; then
  echo "[+] Key matches certificate"
else
  echo "[-] Key does NOT match certificate"
fi
```

## 5. Remote Broker TLS Inspection

### Full TLS handshake with broker
```bash
openssl s_client -connect pulse.n-compass.online:8883 \
  -servername pulse.n-compass.online \
  -showcerts \
  2>&1 | tee /tmp/broker_tls.txt
```

### With client authentication
```bash
openssl s_client -connect pulse.n-compass.online:8883 \
  -servername pulse.n-compass.online \
  -cert ~/pulselink-certs/client_pi_generic.crt \
  -key ~/pulselink-certs/client_pi_generic.key \
  -CAfile ~/pulselink-certs/ca.crt \
  -showcerts \
  2>&1 | tee /tmp/broker_tls_auth.txt
```

### Extract broker certificate chain
```bash
# Get server certificates
echo | openssl s_client -connect pulse.n-compass.online:8883 \
  -servername pulse.n-compass.online 2>/dev/null | \
  sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' > /tmp/broker_chain.pem

# Split chain into individual certs
csplit -f /tmp/broker_cert_ -z /tmp/broker_chain.pem '/-----BEGIN CERTIFICATE-----/' '{*}'

# Analyze each cert
for cert in /tmp/broker_cert_*; do
  echo "=== Certificate ==="
  openssl x509 -in "$cert" -subject -issuer -dates -noout 2>/dev/null
  echo
done
```

### Check what TLS version the broker negotiates
```bash
echo | openssl s_client -connect pulse.n-compass.online:8883 2>/dev/null | \
  grep -E "Protocol|Cipher|Verify"
```

### Test cipher suite strength
```bash
# Check if weak ciphers are accepted
for cipher in RC4-SMD5 DES-CBC3-SHA AES128-SHA AES256-SHA ECDHE-RSA-AES128-SHA; do
  echo -n "$cipher: "
  openssl s_client -connect pulse.n-compass.online:8883 -cipher "$cipher" 2>&1 | \
    grep -c "Cipher is" | sed 's/1/ACCEPTED/' | sed 's/0/rejected/'
done
```

## 6. Certificate Transparency & OSINT

### Check if broker domain has public cert transparency logs
```bash
# Use crt.sh API
curl -s "https://crt.sh/?q=pulse.n-compass.online&output=json" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for entry in data:
    print(f\"{entry['id']} | {entry['issuer_ca_id']} | {entry['not_before']} - {entry['not_after']} | {entry['common_name']}\")
" 2>/dev/null
```

### DNS-based certificate checks
```bash
# Check CAA records (Certificate Authority Authorization)
dig pulse.n-compass.online CAA +short

# Check for certificate-related DNS records
dig pulse.n-compass.online TXT +short
```

## 7. Certificate Reuse Analysis

### If you have certs from multiple devices, compare
```bash
# Compare serial numbers (are they using same cert for all devices?)
for device_cert in device1.crt device2.crt; do
  echo "=== $device_cert ==="
  openssl x509 -in "$device_cert" -serial -subject -noout
done
```

### Extract embedded device identifiers
```bash
# Subject Common Name often contains device ID
openssl x509 -in ~/pulselink-certs/client_pi_generic.crt -subject -noout
# Look for: serial number, device ID, MAC address patterns
```

## 8. Security Implications

| Finding | Risk | Detail |
|---------|------|--------|
| Self-signed CA | Medium | No external trust chain — but expected for IoT |
| Client cert required | **Low Risk** | Good — mutual TLS is enforced |
| Certificate expiry | Check | Are certs near expiration? |
| Same cert for all devices | **High Risk** | One compromise = all devices |
| Weak cipher suites | Check | Which ciphers does broker accept? |
| Key size | Check | RSA 2048+ / EC P-256+ acceptable |
| Cert in firmware | **High Risk** | If certs are baked into firmware, extraction is trivial |

## 9. Key Observation for PulseLink

The Pi has **client certificates at `/opt/pulselink/client_certs/`**. This means:
- The MQTT broker likely requires mutual TLS (mTLS)
- The private key is stored on the Pi filesystem
- Anyone with SSH/root access to the Pi can extract these certs
- **The same cert filename (`client_pi_generic.crt`) suggests shared certificates across devices**
- If so, one compromised Pi = ability to impersonate ANY PulseLink device
