# Security Enhancement Categories

Use this template when generating the "Security Enhancement Recommendations" section of a report.
Pick categories that are relevant to the findings — don't include irrelevant ones just to fill space.

## Network Security

- **Firewall rules:** Restrict inbound/outbound traffic to necessary ports only
- **Network segmentation:** Isolate critical systems (VLANs, subnets)
- **Intrusion detection:** Deploy IDS/IPS at network boundaries
- **DNS security:** Implement DNS filtering, DNSSEC where possible
- **VPN enforcement:** Require VPN for all remote access

## Access Control

- **Principle of least privilege:** Audit and reduce all account permissions
- **Multi-factor authentication:** Enforce MFA on all admin/service accounts
- **Password policy:** Minimum 14 chars, complexity, no reuse, rotation schedule
- **Account lockout:** Lock after 5 failed attempts, progressive backoff
- **Service accounts:** Audit unused accounts, rotate credentials regularly

## System Hardening

- **Patch management:** Implement automated security updates with testing
- **Kernel hardening:** Enable SELinux/AppArmor, restrict kernel modules
- **File integrity:** Deploy AIDE or OSSEC for critical file monitoring
- **Boot security:** Enable Secure Boot, set BIOS/UEFI passwords
- **USB control:** Restrict removable media on sensitive systems

## Application Security

- **Input validation:** Sanitize all user inputs on server side
- **Security headers:** CSP, X-Frame-Options, HSTS, X-Content-Type-Options
- **CSRF protection:** Token-based CSRF defenses on all state-changing endpoints
- **Dependency scanning:** Regular checks for vulnerable libraries (Dependabot, Snyk)
- **WAF:** Deploy web application firewall for public-facing services

## Monitoring & Logging

- **Centralized logging:** Aggregate logs to SIEM (ELK, Splunk, Graylog)
- **Alerting rules:** Create alerts for suspicious patterns (failed logins, privilege escalation)
- **Log retention:** Store logs for minimum 90 days, critical events for 1 year
- **Audit trails:** Log all admin actions, configuration changes, access events
- **Incident response:** Document and test IR playbooks

## Backup & Recovery

- **Encrypted backups:** Encrypt all backup data at rest and in transit
- **3-2-1 rule:** 3 copies, 2 different media, 1 offsite
- **Recovery testing:** Test backup restoration quarterly
- **Ransomware protection:** Air-gapped or immutable backup copies
- **Documentation:** Maintain and test disaster recovery procedures

## Physical Security (Raspberry Pi / IoT Specific)

- **Serial console:** Disable or password-protect UART/JTAG interfaces
- **USB ports:** Disable USB boot or use USBGuard to whitelist devices
- **GPIO access:** Limit physical access to GPIO headers
- **SD card:** Full-disk encryption (LUKS) on removable storage
- **Secure boot:** Enable if supported (Pi 5 supports limited secure boot)

## Wireless Security

- **Encryption:** WPA3-Enterprise where possible, WPA2 minimum
- **Rogue AP detection:** Monitor for unauthorized access points
- **Guest isolation:** Separate guest network from internal resources
- **Bluetooth:** Disable when not in use, limit discoverability
