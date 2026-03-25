# Accuracy Gates

A host/service entry should enter the main enum inventory only if at least one validation gate is met:

- Nmap version detection gives a strong match
- a protocol client confirms the service behavior
- a web endpoint survives soft-404/noise filtering and manual spot-checking
- repeated scans converge on the same result

If not, mark it as:
- candidate
- uncertain
- needs recheck

## Rule
Do not hand vulnerability analysis a fake inventory.
