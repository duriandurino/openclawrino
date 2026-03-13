# OLLAMA_SETUP.md — Local Ollama on Another Kali Machine

Use this to set up Ollama with the xploiter models on a fresh Kali VM.

## 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify it's running:

```bash
ollama --version
curl http://127.0.0.1:11434/api/version
```

## 2. Pull the Pentest Models

These are the two models used by the sub-agents:

```bash
# Light model — recon, enum, reporting, skill crafting
ollama pull xploiter/pentester

# Heavy model — vuln analysis, exploitation, post-exploit
ollama pull xploiter/the-xploiter
```

Verify both are loaded:

```bash
ollama list
# Should show:
#   xploiter/pentester:latest
#   xploiter/the-xploiter:latest
```

## 3. Model Specs

| Model | Size | Context Window | Max Tokens | Used By |
|-------|------|----------------|------------|---------|
| xploiter/pentester | ~1.6 GB | 2,048 | 8,192 | recon, enum, report, skillcrafter |
| xploiter/the-xploiter | ~9.2 GB | 16,384 | 8,192 | vuln, exploit, post |

> **Note:** the-xploiter needs a machine with **12GB+ RAM** for comfortable operation.
> Pentester runs fine on 4GB+ machines.

## 4. OpenClaw Integration

OpenClaw auto-detects Ollama at `http://127.0.0.1:11434`. The agent configs in
`~/.openclaw/agents/*/agent/models.json` already point to this URL.

To verify OpenClaw sees the models:

```bash
openclaw agents list
# Each agent should show Model: ollama/xploiter/pentester or ollama/xploiter/the-xploiter
```

## 5. Performance Tips

- **Preload models** for faster first response:
  ```bash
  ollama run xploiter/pentester ""
  ollama run xploiter/the-xploiter ""
  ```
- **Keep Ollama running** — it's lightweight when idle (~100MB RAM per loaded model)
- **GPU acceleration** — if you have an NVIDIA GPU, Ollama will use it automatically
- **Multiple machines** — Ollama can run on a separate server; just update the `baseUrl` in each agent's `models.json`

## 6. Troubleshooting

| Issue | Fix |
|-------|-----|
| `connection refused` on :11434 | Start Ollama: `ollama serve` |
| Model not found | Pull it: `ollama pull xploiter/pentester` |
| Slow responses | Check RAM usage; heavy model needs 12GB+ |
| Model crashes mid-response | Reduce context or switch to pentester (lighter) |
| `out of memory` | `ollama rm xploiter/the-xploiter` and re-pull, or add swap |

## 7. Systemd Service (Optional)

Ollama installs as a systemd service by default. Check status:

```bash
systemctl status ollama
sudo systemctl enable ollama  # start on boot
```

---

_Specter 🎯 — Pentest Workspace_
