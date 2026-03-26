# Phase Automation Plan — Recon + Enum + Vuln

## Objective

Reduce repeated agent planning by turning common phase workflows into reusable scripts and manifests.

## Design principles

- script the repeatable
- keep agent judgment for ambiguity
- use profile runners for common target types
- standardize outputs for downstream reuse
- prefer wrappers and migration over big rewrites

## Phase priorities

### Recon
Highest ROI:
1. DNS baseline
2. WHOIS summary
3. HTTP fingerprint sweep
4. subdomain collection wrapper

### Enum
Highest ROI:
1. host discovery
2. fast port scan
3. focused service scan
4. SMB baseline enum
5. web baseline enum
6. profile runner

### Vuln
Highest ROI:
1. version to CVE mapping
2. searchsploit wrapper
3. web baseline misconfig checks
4. triage scorer
5. safe NSE-based vuln profiles

## Initial top 10 scripts

1. `scripts/recon/dns/recon_dns_baseline.py`
2. `scripts/recon/whois/recon_whois_summary.sh`
3. `scripts/recon/web/recon_http_fingerprint.sh`
4. `scripts/enum/discovery/discover_hosts_local.sh`
5. `scripts/enum/ports/scan_ports_fast.sh`
6. `scripts/enum/ports/scan_ports_service.sh`
7. `scripts/enum/smb/enum_smb_basic.sh`
8. `scripts/enum/web/enum_web_basic.sh`
9. `scripts/vuln/cve-mapping/map_versions_to_cves.py`
10. `scripts/vuln/web/web_baseline.sh`

## Migration strategy

Existing helpers already live in:

- `recon/scripts/`
- `enum/scripts/`
- `vuln/scripts/`

Recommended approach:

1. keep current scripts working
2. wrap or copy proven logic into new `scripts/` layout
3. add standardized output handling
4. add manifests/profile runners
5. update agent docs to prefer the new scripts

## Next build order

### Step 1
Shared foundation:
- target validation helper
- engagement path helper
- output writer helper
- timestamp helper
- Nmap parser helper

### Step 2
Recon MVP scripts.

### Step 3
Enum MVP scripts.

### Step 4
Vuln MVP scripts.

### Step 5
Manifest-driven orchestration.

## Notes

The goal is not to replace the pentest agents. The goal is to make them stop wasting tokens on boilerplate decisions.
