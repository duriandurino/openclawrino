# SCOPE_player-vault_2026-03-18.md

## Engagement Details

| Field | Value |
|-------|-------|
| **Target** | vault.img (LUKS2 encrypted container on Raspberry Pi 5) |
| **Authorization** | Physical access to Player device |
| **Date** | 2026-03-18 |
| **Tester** | Hatless White (AI Pentest Assistant) |
| **Operator** | The Darkhorse |

## Scope

### In Scope
- vault.img file analysis
- LUKS2 encryption bypass/recovery
- Key management analysis
- Physical security assessment of encryption implementation
- Contents analysis of decrypted vault

### Out of Scope
- Network-based attacks against vault
- Brute-force attacks (time-prohibitive with argon2id)
- Hardware desoldering/memory extraction

## Target Details

| Property | Value |
|----------|-------|
| **File** | `/home/pi/vault.img` |
| **Encryption** | LUKS2 (AES-XTS-plain64, 512-bit) |
| **UUID** | `9757eca5-e8a1-4f8a-9c20-8c9252d61d09` |
| **PBKDF** | argon2id |
| **Key Slots** | 8 total, 1 in use |
| **Mount Point** | `/home/pi/n-compasstv-secure` |
| **Cryptsetup Version** | 2.6.0 |

## Authorization

This engagement is authorized under the existing physical access agreement for Player penetration testing. The vault was accessed using device-specific hardware identifiers discovered through code analysis.
