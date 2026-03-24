# Engagement: G9 Live
- **Authorized by:** Operator-requested live enum -> vuln -> report engagement in main session
- **Date:** 2026-03-24
- **Targets:** PC G9 (`192.168.0.227`) on local network
- **Out of scope:** Destructive actions, denial of service, persistence, credential spraying, social engineering, exploitation unless separately authorized
- **Rules:** Enumeration and vulnerability analysis are authorized for this engagement. Reporting should include only live-verified observations and clearly separate confirmed findings from hypotheses.

## Discovery Note
- **Hostname verification:** `nbtscan 192.168.0.0/24` identified `192.168.0.227` as `G9`
- **Verification status:** ✅ verified live
