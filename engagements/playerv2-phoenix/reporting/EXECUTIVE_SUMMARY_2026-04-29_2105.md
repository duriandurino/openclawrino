# Executive Summary — Player v2 Phoenix

**Classification:** Confidential
**Target:** playerv2-phoenix
**Date:** 2026-04-29 21:05 GMT+8

## Overview

This assessment found a verified local compromise chain in the Phoenix player device. The design intended to bind access to trusted hardware and protected storage, but that control was bypassed by changing only how the same trusted microSD card was presented to the Raspberry Pi.

When the card was booted through an external USB SD adapter, Phoenix still attempted startup but its hardware-check process depended on a fixed Linux device path that no longer existed. Instead of denying access safely, the device crashed into a more accessible state and preserved local GUI and shell access.

From that foothold, the engagement recovered sensitive provisioning material from shell history and successfully reached the protected Phoenix vault in read-only mode using the product's own trust inputs and derivation logic. This exposed hidden runtime files, database key material, license metadata, playlist structures, and a real Ed25519 private key.

## Top findings

1. **PHX-V01 — Storage-interface-dependent authorization failure**  
   The trusted-media check depended on a fixed block-device path rather than a transport-independent media identity check.

2. **PHX-V02 — Fail-open local access after hardware-check crash**  
   When Phoenix could not read the expected hardware identity path, the authorization component crashed and preserved local shell and GUI access instead of failing closed.

3. **PHX-V03 — Sensitive provisioning artifact exposure in shell history**  
   Local shell history retained a plaintext provisioning command, setup host, and passphrase that remained operationally meaningful during the engagement.

## Why this matters

The main risk is not just a local bypass. The bypass leads directly to:
- retained local OS access
- exposure of provisioning secrets and workflow details
- access to protected vault-backed runtime material
- recovery of private-key and database-key material
- weakened confidence in device cloning resistance, physical access protection, and trusted runtime isolation

## Business impact

An attacker with physical access to a Phoenix device could move from local handling of the media to practical compromise of protected runtime material without modifying the underlying player image. This threatens:
- endpoint trust and device authorization assumptions
- secret and license protection
- protected media and playlist handling
- service integrity and operational confidence

## Severity snapshot

- PHX-V01: **Medium**
- PHX-V02: **High**
- PHX-V03: **High**

## Immediate priorities

- Make media-identity validation independent of Linux block-device naming.
- Ensure any authorization-check failure fails closed and suppresses local shell and GUI access.
- Remove and rotate exposed provisioning secrets and bootstrap material.
- Review protected key placement and vault derivation logic to reduce recovery after local compromise.

## Cleanup and testing posture

The deeper vault work was performed read-only. No destructive writes, brute-force actions, or persistence changes were introduced as part of the validated attack chain.

## Final assessment

Phoenix currently has a verified physical-to-local attack path that can extend into protected secret and runtime recovery. The highest-value fixes are fail-closed authorization handling, transport-independent trusted-media validation, and immediate secret rotation and provisioning hygiene improvements.
