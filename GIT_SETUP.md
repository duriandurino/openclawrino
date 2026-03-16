# GIT_SETUP.md — Full Git + OpenClaw Workspace Setup on Kali Linux

Use this to fully set up the pentest workspace on a fresh Kali machine or VM.

---

## Prerequisites (Fresh Kali)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git git-lfs curl wget gnupg2 software-properties-common

# (Optional) Install SSH keys if you use git over SSH
sudo apt install -y openssh-client
```

### Git Global Identity (One-Time Setup)

```bash
git config --global user.name "Durin"
git config --global user.email "durin0@users.noreply.github.com"
git config --global init.defaultBranch main
git config --global pull.rebase true          # Rebase on pull (cleaner history)
git config --global credential.helper store   # Cache PAT for push access
```

---

## OpenClaw Installation

```bash
# Install Node.js (required for OpenClaw)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt install -y nodejs

# Verify
node -v   # Should be v22.x+
npm -v

# Install OpenClaw globally
npm install -g openclaw

# Verify
openclaw --version
```

---

## Workspace Setup

This creates the workspace directory structure. **OpenClaw does NOT auto-create it** — you need to clone or set it up manually.

### Option A: Clone from GitHub (Recommended)

```bash
# Create parent directory
mkdir -p ~/.openclaw

# Clone with PAT for full read/write access
# Replace <YOUR_PAT> with your fine-grained GitHub token
git clone https://<YOUR_PAT>@github.com/duriandurino/openclawrino.git ~/.openclaw/workspace

# Navigate into it
cd ~/.openclaw/workspace
```

### Option B: Clone via SSH (If SSH key is set up)

```bash
mkdir -p ~/.openclaw
git clone git@github.com:duriandurino/openclawrino.git ~/.openclaw/workspace
cd ~/.openclaw/workspace
```

### Option C: Clone without PAT, add later

```bash
mkdir -p ~/.openclaw
git clone https://github.com/duriandurino/openclawrino.git ~/.openclaw/workspace
cd ~/.openclaw/workspace

# Add PAT for push access
git remote set-url origin https://<YOUR_PAT>@github.com/duriandurino/openclawrino.git
```

---

## Cipher Workspace (Separate)

The cipher agent (Second in Command) uses a separate workspace to isolate coding tasks from pentest operations.

```bash
# Create the cipher workspace directory (NOT auto-created)
mkdir -p ~/.openclaw/workspace-coder

# It starts empty — OpenClaw agents create their own files there
```

---

## PAT (Personal Access Token) Setup

You need a GitHub PAT for push access to the repo.

### Create a Fine-Grained PAT

1. Go to **GitHub → Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Set permissions:
   - **Repository access:** Select `openclawrino`
   - **Contents:** Read and Write
   - **Metadata:** Read (auto-included)
4. Generate and **copy the token** — you won't see it again

### Store the PAT

```bash
# Option 1: Credential helper (recommended)
git config --global credential.helper store
# First push will prompt — enter your PAT as username, 'x' as password

# Option 2: Embed in remote URL
cd ~/.openclaw/workspace
git remote set-url origin https://<YOUR_PAT>@github.com/duriandurino/openclawrino.git
```

⚠️ **Never commit or push the PAT to the repo.**

---

## Verify Everything

```bash
# Check git config
git config --global --list | grep user
git config --global --list | grep credential

# Check workspace
cd ~/.openclaw/workspace
git status
git remote -v
ls -la

# Check cipher workspace
ls -la ~/.openclaw/workspace-coder

# Check OpenClaw
openclaw --version
openclaw status
```

---

## Start OpenClaw

```bash
openclaw gateway start
openclaw status
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `403 Permission denied` | PAT needs **Contents: Read and write** on the repo |
| `404 Not found` | Repo doesn't exist or PAT has no access |
| `secret scanning push protection` | Disable in repo Settings → Code security → Push protection |
| `npm ERR!` on install | Run `npm install -g openclaw` with `--force` or use `sudo` |
| `openclaw: command not found` | Rehash shell: `hash -r` or restart terminal |
| Workspace not recognized | Ensure `~/.openclaw/workspace` is the cloned repo |
| cipher sees same workspace | Check `openclaw.json` → `agents.list` → cipher/specter-coder `workspace` field should be `/home/<user>/.openclaw/workspace-coder` |

---

_Updated by Hatless White 🎯 — Primordial Pentest Assistant_
