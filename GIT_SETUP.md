# GIT_SETUP.md — Clone Workspace on Another Kali Machine

Use this to pull the pentest workspace on a fresh Kali VM.

## 1. Prerequisites

```bash
sudo apt update && sudo apt install -y git
```

## 2. Clone the Repo

```bash
# Using your GitHub PAT (fine-grained, needs Contents: Read & Write)
git clone https://<YOUR_PAT>@github.com/duriandurino/openclawrino.git ~/.openclaw/workspace

# Or clone first, then set remote
git clone https://github.com/duriandurino/openclawrino.git ~/.openclaw/workspace
cd ~/.openclaw/workspace
```

## 3. Configure Git Identity

```bash
git config user.name "Specter"
git config user.email "specter@openclaw.local"
```

## 4. PAT Setup (Optional — for push access)

### Option A: Credential Helper (Recommended)

```bash
git config --global credential.helper store
# Next push will prompt for username/password:
#   username: github_pat_<YOUR_TOKEN>
#   password: x
```

### Option B: Embed in Remote URL

```bash
git remote set-url origin https://<YOUR_PAT>@github.com/duriandurino/openclawrino.git
```

⚠️ **Never commit the PAT to the repo.** The `.gitignore` excludes sensitive files, but embedding tokens in git config is visible locally.

## 5. Verify

```bash
git status
git remote -v
```

## 6. OpenClaw Integration

If running OpenClaw on this machine too, symlink or set the workspace:

```bash
# OpenClaw looks for workspace at ~/.openclaw/workspace by default
# The cloned repo IS the workspace — you're good.
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `403 Permission denied` | PAT needs **Contents: Read and write** in repo permissions |
| `404 Not found` | Repo doesn't exist or PAT has no access to this repo |
| `secret scanning push protection` | Disable in repo Settings → Code security → Push protection |

---

_Specter 🎯 — Pentest Workspace_
