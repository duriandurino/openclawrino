# Post-Exploitation Phase Essentials Examples — Real User Triggers

## Example 1: Keep post-exploitation disciplined
**User:** "Do post-exploitation safely and methodically"
**Expected:** Focus on impact assessment, evidence quality, scope discipline, and minimal necessary activity.

## Example 2: Explain what post-exploitation is for
**User:** "What is the goal of post-exploitation in a pentest?"
**Expected:** Explain impact assessment after foothold, not freestyle hacking.

## Example 3: Decide what to do after getting a shell
**User:** "We have a shell. What's the right post-exploitation workflow?"
**Expected:** Stabilize, orient, assess privilege, discover reachable value, evaluate lateral movement, document artifacts, and respect ROE.

## Example 4: Defensible evidence gathering
**User:** "How should I gather proof without overdoing it?"
**Expected:** Prefer proof-of-access, minimal data handling, strong documentation, and defender-relevant evidence.

## Example 5: Lateral movement and persistence scope discipline
**User:** "How should I think about lateral movement or persistence in an authorized test?"
**Expected:** Explain them as scoped validation tasks with strong stop conditions and high reporting value.

## Example 6: Telemetry-aware post-exploitation
**User:** "What logs and detections should defenders see from post-exploitation?"
**Expected:** Tie behaviors to ATT&CK-style tactics and OS telemetry like Sysmon, security events, and auditd.

## Example 7: Cleanup and reporting
**User:** "What should I clean up and report after post-exploitation?"
**Expected:** Remove tester-introduced artifacts as agreed, preserve evidence, and report access paths, impact, and residual risk.
