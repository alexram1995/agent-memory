# Agent Memory Orchestrator (starter)

SQLite-backed persistent memory and checkpoint CLI for an agent using Ollama. This is a prototype, not yet an OpenCode integration.

## Setup (PowerShell)

```powershell
cd agent-memory
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
ollama pull qwen3.5:9b
```

Edit `config.yaml` (model tag, context size, Ollama URL, DB path). Verify GPU placement using `ollama ps` and `nvidia-smi`; this program does not force GPU placement, Ollama controls placement.

## CLI examples

```powershell
agent-memory start automotive-twin
agent-memory remember automotive-twin constraint "Use PowerShell examples; no Bash" --importance 5
agent-memory event automotive-twin test "Unit tests passed" --verified
agent-memory recover automotive-twin "CAN gateway message routing"
agent-memory checkpoint automotive-twin --file session-notes.md
```

The `checkpoint` command uses Qwen to create/update active state. The `recover` command assembles active state, matching FTS memory and recent events into a text payload. It prints that payload; integration into OpenCode is a follow-on task.

## Limitations

- FTS5 only; no vector embeddings yet.
- Retrieval is lexical and intentionally simple.
- Checkpoint command input is notes/file content, not automatically the OpenCode transcript.
- A single asyncio lock serializes requests made through this process only. It does **not** lock Ollama against OpenCode or other clients. To enforce global serialization, OpenCode must use this gateway or share a coordination mechanism.
- The checkpoint prompt is basic; review generated state before relying on it.
- `active_states` is one current checkpoint per project.
