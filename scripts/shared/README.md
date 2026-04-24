# shared/

Shared utilities used by multiple phases.

## Planned subdirectories

- `lib/` - validation, path helpers, output helpers, target-family composition helpers
- `parsers/` - parse tool output into JSON
- `templates/` - markdown/json templates
- `manifests/` - reusable workflow profiles
- `target-types/` - full-pentest target family definitions and composition notes
- `test-data/` - sample outputs for parser tests

## What belongs here

- target normalization
- target-family composition and recommendations for full pentests
- timestamp generation
- engagement path creation
- dependency checks
- structured output writers
- result summarizers
- common parsers like Nmap -> JSON

## Rule

If recon + enum + vuln could all use it, put it here.
