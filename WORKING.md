# WORKING.md

## Current objective
Persist the most important recent session context so a fresh session can resume cleanly after reset

## Current task
Define and wire the new /remember soft command for reset-safe recall

## Key context
- User wants a new /remember soft command that immediately remembers key recent session context.
- The /remember behavior has been documented in the soft-command spec and mapped to the durable context harness.
- Next likely step is implementing behavior-layer handling so typing /remember triggers this flow automatically.

## Exact next actions
- Implement runtime behavior so /remember invokes the durable snapshot flow automatically.
- Keep the saved context concise and focused on current task, objective, and immediate next action.

## Critical files
- docs/pentest-command-spec.md
- docs/context-harness.md
