# Engagement: G8 Live
- **Authorized by:** Operator-requested live recon -> enum -> vuln -> report engagement in main session
- **Date:** 2026-03-25
- **Targets:** PC G8 (`192.168.0.108`) on local network
- **Out of scope:** Destructive actions, denial of service, persistence, credential spraying, social engineering, exploitation unless separately authorized
- **Rules:** Reconnaissance, enumeration, vulnerability analysis, and reporting are authorized for this engagement. Reporting should include only live-verified observations and clearly separate confirmed findings from hypotheses.

## Discovery Note
- **Hostname verification:** `nbtscan 192.168.0.0/24` identified `192.168.0.108` as `G8`
- **Verification status:** ✅ verified live
