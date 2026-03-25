# Secrets Note

The full Second Life snapshot includes sensitive local files.

Those files are stored locally under:
- `second-life/copies-private/`

They are intentionally **gitignored** and are **not pushed** to GitHub.

Reason:
- they may contain OAuth credentials
- provider secrets
- pairing data
- machine/node identity material

Use the docs in this folder plus the local `copies-private/` directory together when migrating to a new PC.
