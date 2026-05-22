# 🧠 MiMo Reasoning Playground

Interactive exploration tool for Xiaomi's **MiMo v2.5 Pro** reasoning model.
Watch chain-of-thought reasoning unfold in real-time, compare reasoning modes,
and stress-test with built-in challenges.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Model](https://img.shields.io/badge/model-MiMo%20v2.5%20Pro-purple)

## ✨ Features

- 🧠 **Real-time reasoning trace** — watch the model think step-by-step
- 🎯 **10 built-in challenges** — logic, math, code, philosophy, analysis
- ⚖️ **Mode comparison** — run same prompt through 6 different reasoning styles
- 🌐 **Web UI** — Gradio-based interactive playground
- 💻 **CLI** — terminal-native experience for power users
- 📊 **Token metrics** — track reasoning tokens, latency, step count

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/YOUR_USERNAME/mimo-reasoning-playground.git
cd mimo-reasoning-playground
pip install -e .
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API credentials
```

### 3. Run

**Web UI:**
```bash
mimo-playground web
# Opens at http://localhost:8501
```

**CLI:**
```bash
# List challenges
mimo-playground list

# Run a challenge
mimo-playground run logic-001

# Interactive chat
mimo-playground chat

# Quick question
mimo-playground ask "Explain the Monty Hall problem"
```

## 🎯 Challenges

| ID | Title | Category | Difficulty |
|----|-------|----------|------------|
| logic-001 | The Missing Dollar | Logic | medium |
| logic-002 | Monty Hall Problem | Logic | medium |
| math-001 | Infinite Series | Math | hard |
| math-002 | Combinatorial Proof | Math | hard |
| code-001 | Find the Bug | Code | medium |
| code-002 | Algorithm Complexity | Code | hard |
| philo-001 | Ship of Theseus | Philosophy | medium |
| philo-002 | Trolley Problem Variants | Philosophy | hard |
| real-001 | Crypto Market Analysis | Analysis | hard |
| real-002 | System Design | Engineering | extreme |
| creative-001 | Constraint Poetry | Creative | medium |

## 🏷️ Reasoning Modes

| Mode | Description |
|------|-------------|
| **Default** | MiMo's natural reasoning style |
| **Step-by-Step** | Explicit sequential breakdown |
| **Socratic** | Self-questioning, explores assumptions |
| **Adversarial** | Argues both sides before concluding |
| **ELI5** | Simple analogies, concrete examples |
| **Academic** | Formal logic, citations, precise definitions |

## 📁 Project Structure

```
mimo-reasoning-playground/
├── mimo_playground/
│   ├── __init__.py       # Package init
│   ├── client.py         # Async MiMo API client with streaming
│   ├── challenges.py     # Pre-built reasoning challenges
│   ├── app.py            # Gradio web UI
│   └── cli.py            # CLI entry point
├── tests/
│   └── test_client.py    # Unit tests
├── .env.example          # Environment template
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
├── LICENSE               # MIT
└── README.md             # This file
```

## 🔌 API Usage

```python
import asyncio
from mimo_playground.client import MiMoClient

client = MiMoClient(
    api_base="https://api.xiaomi.com/v1",
    api_key="your-key",
)

async def main():
    async for event in client.stream_reasoning("Explain quantum entanglement"):
        if event["type"] == "reasoning":
            print(f"🧠 {event['content']}", end="")
        elif event["type"] == "answer":
            print(f"💡 {event['content']}", end="")

asyncio.run(main())
```

## 🛠️ Tech Stack

- **Python 3.10+** — async/await throughout
- **httpx** — async HTTP streaming
- **Gradio 4+** — web UI with dark theme
- **MiMo v2.5 Pro** — Xiaomi's reasoning model

## 📄 License

MIT — see [LICENSE](LICENSE)

## 🙏 Credits

Built to explore the reasoning capabilities of [Xiaomi MiMo](https://github.com/XiaomiMiMo).

---

*Watch the model think. Understand how it reasons.*
