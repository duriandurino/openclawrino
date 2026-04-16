# Large File Inventory for Manual Review / Zipping

This list is for files that are either large, binary, awkward to diff, sensitive, or likely better moved manually than relied on through normal git history.

## Definitely manual-copy if you want them

### Gitignored / excluded by policy
- `memory/` (entire folder)
- `credentials.json`
- `.google-creds`
- `*.pcap`, `*.pcapng`, `*.cap`
- `*.key`, `*.pem`, `*.cred`
- `*.hash`, `*.john`
- `*.log`

### Notable evidence captures
- `engagements/player-v2/recon/capture-extended.pcap`
- `engagements/player-v2/recon/capture-full.pcap`
- `engagements/player-v2/recon/capture-broad.pcap`

## Large tracked text or artifact files worth reviewing
These are in git or visible in the repo, but you may still want a manual archive for safety or to keep repo history lean going forward.

### Very large tracked files
- `engagements/_archive/quick-scan/quick-windows-host-2026-03-27_0944/vuln/raw/searchsploit-auto-nmap-service-192-168-0-112-2026-03-27-094500-2026-03-27_094736.txt` (~13 MB)
- `engagements/_archive/quick-scan/quick-windows-host-retest-2026-03-27_0955/vuln/raw/searchsploit-auto-nmap-service-192-168-0-112-2026-03-27-095622-2026-03-27_095857.txt` (~13 MB)

### Report binaries and exports, many of them
Common hotspots:
- `engagements/**/reporting/*.docx`
- `engagements/**/reporting/*.pptx`
- `engagements/**/reporting/*.pdf`
- `slides/**/*.pptx`
- `research/**/*.pdf`

High-churn examples:
- `engagements/hardwarelockv2/06-report/`
- `engagements/player-network/reporting/`
- `engagements/player-vault/reporting/`
- `engagements/quick-*/quick-scan/reporting/`
- `engagements/_archive/quick-scan/**/reporting/`

## Untracked report outputs currently present
These will not move unless committed or copied manually.

### Archive quick-scan outputs
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1759.docx`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1759.md`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1759.pptx`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1759.publish.json`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1801.docx`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1801.md`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1801.pptx`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1801.publish.json`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1810.docx`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1810.md`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1810.pptx`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/REPORT_FINAL_QUICK_SCAN_2026-04-13_1810.publish.json`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/findings-quick-scan-2026-04-13_1759.json`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/findings-quick-scan-2026-04-13_1801.json`
- `engagements/_archive/quick-scan/quick-onlinebookfair-net-2026-04-07_1831-fix/quick-scan/reporting/findings-quick-scan-2026-04-13_1810.json`

### hardwarelockv2 untracked outputs
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1603.docx`
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1603.md`
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1603.pptx`
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1603.publish.json`
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1608.docx`
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1608.md`
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1608.pptx`
- `engagements/hardwarelockv2/06-report/REPORT_FINAL_hardwareLockV2_2026-04-14_1608.publish.json`

## Recommendation
If the new always-on machine is meant to be clean and maintainable:
- keep source, skills, agent definitions, scripts, docs, and core markdown in git
- keep `memory/`, creds, packet captures, bulky report exports, and external auth material in a manual archive or secondary storage
- consider future `.gitignore` expansion for repetitive `*.docx` and `*.pptx` report outputs if repo bloat becomes annoying
