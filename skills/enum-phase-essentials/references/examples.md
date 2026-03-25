# Enumeration Phase Essentials Examples — Real User Triggers

## Example 1: Speed up enumeration without losing confidence
**User:** "How do I enumerate faster without getting garbage results?"
**Expected:** Recommend a fast-discovery then targeted-validation pipeline with explicit confidence gates.

## Example 2: Explain Masscan vs Nmap workflow
**User:** "When should I use Masscan vs Nmap in enum?"
**Expected:** Explain Masscan as candidate generation and Nmap as validation/enrichment.

## Example 3: Tune enumeration safely
**User:** "How should I tune scan speed and retries?"
**Expected:** Explain rate, retries, version intensity, and why accuracy can collapse if tuning is too aggressive.

## Example 4: Structure an enumeration phase
**User:** "Do the enumeration phase methodically"
**Expected:** Apply scope -> target hygiene -> host discovery -> port discovery -> service validation -> protocol deep dive -> correlation.

## Example 5: Reduce false positives
**User:** "How do I stop enum from lying to me?"
**Expected:** Use multi-signal confirmation, anti-soft-404 filtering, handshake validation, and selective rescans.

## Example 6: Web enum workflow
**User:** "What's the fastest safe way to map web attack surface?"
**Expected:** Use mapping first, then content discovery, then response filtering and validation.

## Example 7: Windows/AD enum workflow
**User:** "How should I enumerate SMB/RPC/LDAP correctly?"
**Expected:** Use service-triggered deep dives with enum4linux, smbclient, rpcclient, LDAP-aware tooling, and validation steps.
