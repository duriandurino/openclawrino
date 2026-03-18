# GIT_SETUP_WIN11.md — Full Git + OpenClaw Workspace Setup on Windows 11

Use this to set up the pentest workspace on a Windows 11 laptop.

---

## Prerequisites (Fresh Windows 11)

### 1. Install Windows Terminal (if not present)
Windows 11 includes it by default. If missing:
```powershell
# From PowerShell (Admin)
winget install Microsoft.WindowsTerminal
```

### 2. Install Git for Windows
```powershell
winget install Git.Git
```
Or download from: https://git-scm.com/download/win

During install, select:
- Default editor: **Vim** or **nano** (your choice)
- Initial branch: **main**
- PATH environment: **Git from the command line and also from 3rd-party software**
- SSH executable: **Use bundled OpenSSH**
- HTTPS transport: **Use the OpenSSL library**
- Line endings: **Checkout Windows-style, commit Unix-style**
- Terminal emulator: **Use Windows' default console window** (or MinTTY if preferred)
- `git pull` behavior: **Rebase**
- Credential helper: **Git Credential Manager**
- Extra options: Enable file system caching

### 3. Install Node.js
```powershell
winget install OpenJS.NodeJS.LTS
```
Or download LTS from: https://nodejs.org

Verify:
```powershell
node -v   # Should be v22.x+
npm -v
```

### 4. (Optional) Install Python (needed for some pentest tools)
```powershell
winget install Python.Python.3.12
```

### 5. (Optional) Install Nmap
```powershell
winget install Insecure.Nmap
```

---

## Git Global Identity (One-Time Setup)

Open **Git Bash** (installed with Git) or **Windows Terminal**:

```powershell
git config --global user.name "Durin"
git config --global user.email "durin0@users.noreply.github.com"
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global credential.helper manager   # Uses Git Credential Manager (GUI prompt)
```

### Set Default Branch to Main
```powershell
git config --global init.defaultBranch main
```

---

## OpenClaw Installation

```powershell
# Install OpenClaw globally via npm
npm install -g openclaw

# Verify
openclaw --version
```

### If npm global path not in PATH:
```powershell
# Find where npm installs globally
npm config get prefix

# Add to PATH (PowerShell Admin):
$npmPath = npm config get prefix
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$npmPath", [EnvironmentVariableTarget]::User)

# Restart terminal after
```

---

## Workspace Setup

### Option A: Clone from GitHub (Recommended)

```powershell
# Create .openclaw directory
mkdir "$env:USERPROFILE\.openclaw"

# Clone the repo
git clone https://github.com/duriandurino/openclawrino.git "$env:USERPROFILE\.openclaw\workspace"

# Navigate into it
cd "$env:USERPROFILE\.openclaw\workspace"
```

### Option B: Clone with PAT (for push access without GUI prompt)

```powershell
mkdir "$env:USERPROFILE\.openclaw"
git clone https://<YOUR_PAT>@github.com/duriandurino/openclawrino.git "$env:USERPROFILE\.openclaw\workspace"
cd "$env:USERPROFILE\.openclaw\workspace"
```

### Option C: Clone via SSH (if SSH key is set up)

```powershell
mkdir "$env:USERPROFILE\.openclaw"
git clone git@github.com:duriandurino/openclawrino.git "$env:USERPROFILE\.openclaw\workspace"
```

---

## Cipher Workspace (Separate)

```powershell
mkdir "$env:USERPROFILE\.openclaw\workspace-coder"
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
Git Credential Manager (installed with Git for Windows) will prompt you on first push. Enter:
- **Username:** your PAT (or just paste it)
- **Password:** leave blank or enter `x`

Or embed it in the remote URL:
```powershell
cd "$env:USERPROFILE\.openclaw\workspace"
git remote set-url origin https://<YOUR_PAT>@github.com/duriandurino/openclawrino.git
```

⚠️ **Never commit or push the PAT to the repo.**

---

## Ollama Setup (for local AI models)

If you want local pentest models (xploiter) on your laptop:

```powershell
# Install Ollama for Windows
winget install Ollama.Ollama

# Pull the pentest models
ollama pull xploiter/pentester
ollama pull xploiter/the-xploiter

# Verify
ollama list
```

---

## Verify Everything

```powershell
# Check git config
git config --global --list | Select-String "user|credential"

# Check workspace
cd "$env:USERPROFILE\.openclaw\workspace"
git status
git remote -v
dir

# Check cipher workspace
dir "$env:USERPROFILE\.openclaw\workspace-coder"

# Check OpenClaw
openclaw --version
openclaw status
```

---

## Start OpenClaw

```powershell
openclaw gateway start
openclaw status
```

---

## Windows-Specific Notes

### PowerShell vs Git Bash
- **PowerShell** — Use for most commands, OpenClaw CLI
- **Git Bash** — Use if you need Unix-style commands (grep, awk, etc.)
- Both work for git operations

### Path Shortcuts
| Shortcut | Path |
|----------|------|
| Workspace | `%USERPROFILE%\.openclaw\workspace` |
| Cipher workspace | `%USERPROFILE%\.openclaw\workspace-coder` |
| Git config | `%USERPROFILE%\.gitconfig` |
| OpenClaw config | `%USERPROFILE%\.openclaw\openclaw.json` |

### Defender Exclusions (Recommended)
Windows Defender can slow down npm/git operations:
```powershell
# PowerShell (Admin) — add exclusions
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.openclaw"
Add-MpPreference -ExclusionPath "$env:USERPROFILE\AppData\Roaming\npm"
```

### WSL2 (Optional)
If you want a Linux environment on Windows:
```powershell
wsl --install
# Restart, then follow GIT_SETUP.md (Linux version) inside WSL
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `npm ERR!` on install | Run PowerShell as Administrator, or use `npm install -g openclaw --force` |
| `openclaw: command not found` | Restart terminal, or check `npm config get prefix` is in PATH |
| `403 Permission denied` | PAT needs **Contents: Read and write** on the repo |
| Git line ending warnings | Already handled by `core.autocrlf` default on Windows |
| `cannot execute binary` | Windows can't run Linux ELF binaries — use WSL2 or native Windows tools |
| Node.js EACCES error | Run PowerShell as Administrator |
| npm prefix not in PATH | See "Set Default Branch" section above |

---

## Quick Reference Card

```powershell
# === ONE-TIME SETUP ===
winget install Git.Git
winget install OpenJS.NodeJS.LTS
npm install -g openclaw

git config --global user.name "Durin"
git config --global user.email "durin0@users.noreply.github.com"
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global credential.helper manager

# === EVERY TIME (new machine) ===
mkdir "$env:USERPROFILE\.openclaw"
git clone https://github.com/duriandurino/openclawrino.git "$env:USERPROFILE\.openclaw\workspace"
mkdir "$env:USERPROFILE\.openclaw\workspace-coder"

# === START ===
openclaw gateway start
openclaw status
```

---

_Created by Hatless White 🎯 — For The Darkhorse's Windows 11 setup_
