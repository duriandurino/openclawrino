# Post Skill — Usage Examples (Phase 0)

## Example 1: Initial Shell Assessment
- **User:** "I got a shell, now what?"
- **Action:** Run position recon — whoami, uname, ip addr, ps aux, environment
- **Resources:** scripts/privesc_check.py

## Example 2: Privilege Escalation
- **User:** "How do I escalate to root on this host?"
- **Action:** Check SUID, sudo -l, capabilities, kernel version, cron jobs
- **Resources:** scripts/privesc_check.py, references/privesc_reference.md

## Example 3: Credential Harvesting
- **User:** "Find all credentials on this machine"
- **Action:** Search config files, SSH keys, bash history, /etc/shadow, web configs
- **Resources:** grep, find, cat commands

## Example 4: Lateral Movement
- **User:** "Move laterally from this host to others on the network"
- **Action:** Discover network, check for SSH keys, set up pivot with SSH tunnels
- **Resources:** SSH tunneling, proxychains, crackmapexec

## Example 5: Persistence
- **User:** "Set up persistence on this host"
- **Action:** Add SSH key, create cron job, plant systemd service (if authorized)
- **Resources:** cron, systemctl, SSH key injection

## Example 6: Data Gathering
- **User:** "Gather all interesting data from this machine for the report"
- **Action:** System info, user accounts, network config, interesting files
- **Resources:** System commands, find, grep

## Example 7: Pivot Through Host
- **User:** "Pivot through this host to scan the internal network"
- **Action:** SSH dynamic port forward + proxychains for internal scanning
- **Resources:** SSH -D, proxychains, nmap
