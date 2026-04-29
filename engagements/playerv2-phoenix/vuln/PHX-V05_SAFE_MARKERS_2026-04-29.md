# PHX-V05 Safe Marker Pack

Date: 2026-04-29
Purpose: Provide benign marker ideas for PHX-V05 recovery-path validation.

## Marker design goals

Markers should be:
- harmless
- easy to recognize
- hard to confuse with normal Phoenix content
- non-persistent beyond the test unless copied by the recovery path
- safe to document in screenshots and notes

## Recommended marker strings

### Console marker
`PHX-V05 SAFE MARKER: operator-controlled recovery path reached`

### File marker content
`PHX-V05 benign marker copied during controlled recovery-path validation on 2026-04-29`

### Alternate short marker
`PHX-V05_MARKER_OK`

## Recommended marker file names

Use only one or two, not a whole set.

### Preferred options
- `/home/pi/PHX-V05_MARKER.txt`
- `/opt/PHX-V05_MARKER.txt`
- `/var/tmp/PHX-V05_MARKER.txt`

### Why these are good
- easy to find later
- clearly test-related
- non-executable
- minimal ambiguity if copied to sacrificial media

## Marker use guidance

### For Level A
Use the console marker inside a safely instrumented recovery script that exits before real write actions.

### For Level B
Use a single benign marker file in the USB runtime so that, if copied, it proves the `rsync` trust path wrote operator-controlled content to the sacrificial SD.

## Do not use

Avoid markers that:
- modify startup or persistence behavior
- look like malware or backdoors
- alter authentication logic
- depend on binaries, cron, systemd services, or shell startup hooks
- could accidentally change user experience in a misleading way

## Documentation reminder

When a marker is used, always record:
- exact file path
- exact content
- whether it appeared only in console output or was copied to target media
- whether the target was primary media or sacrificial media
