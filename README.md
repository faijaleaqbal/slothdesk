# 🦥 SlothDesk: The Autonomous Zero-Cloud Desktop Butler

> **"Move slow. Do nothing. Let local open-weight AI tame your digital hoard."**  
> *Built for Hacktoberfest Open-Source AI Challenge (Week 3: Slow and Steady) — Celebrating International Sloth Day (October 20).*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688.svg)](https://fastapi.tiangolo.com)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20On--Device-success.svg)](#why-open-innovation-matters)
[![Models](https://img.shields.io/badge/Models-Ollama%20%7C%20Llama%203.2%20%7C%20Qwen%202.5%20%7C%20SmolLM-orange.svg)](#open-source-ai-core)

---

## 🛋️ Why SlothDesk?

Sloths sleep 15 to 20 hours a day and move at a relaxed 0.15 mph. They understand the fundamental truth of thermodynamics: **never expend energy on something that doesn't need doing.**

Yet as developers and digital workers, we waste hours of our precious lives:
- Manually sorting `Downloads` folders filled with `Screenshot_2026-10-20_at_2.31.png` and `invoice_final_v2(3).pdf`.
- Skimming 30-page PDF contracts and utility statements just to find the total due.
- Agonizing over directory structures and tags.
- Procrastinating filing receipts until tax season turns into an existential crisis.

**SlothDesk is built to reward pure laziness.** You dump everything into one folder (the *Sloth Den*) and walk away. SlothDesk's autonomous local daemon wakes up periodically, digests your clutter using **local open-weight AI**, gives every file a sensible descriptive name, files it into structured categories, generates a hilarious 1-sentence **Sloth TL;DR**, and computes how many **Sloth Naps** you earned by doing absolutely nothing.

And because it is built entirely on open-source AI, **your confidential tax returns, medical lab results, and private invoices never leave your laptop.**

---

## ✨ Features

- 🦥 **Autonomous Semantic Triage**: Classifies documents into `Finance`, `Work`, `Personal`, `Code`, `Reading`, and `Media` based on content semantics, not just file extensions.
- 🏷️ **Smart ISO Auto-Renaming**: Renames chaotic files into standardized, searchable names like `2026-10-20_finance_invoice_aws_september_final_v2.txt`.
- 😴 **The Sloth Energy Meter**: Quantifies human suffering avoided! Tracks minutes of manual filing saved, calories conserved, and converts your laziness into **"Naps Earned"** (1 nap = 15 minutes of saved effort).
- 💬 **"Ask My Clutter" (100% Local RAG)**: Ask plain-English questions about your hoard without opening a single folder:
  - *"How much did AWS charge me this month?"*
  - *"What are the action items from the Q4 strategy meeting?"*
  - *"Where are my cholesterol test results?"*
- ⚡ **Zero-Cloud & Zero Marginal Cost**: Powered by local open weights (Ollama, Llama 3.2, Qwen 2.5, SmolLM2) with a built-in embedded offline NLP engine. Costs **$0.00** to run 24/7.
- ↩️ **1-Click Safety Undo**: Accidental move? Every operation is logged in an ACID SQLite database and can be reversed with a single click or CLI command.
- 🎨 **Cozy Sloth Web Dashboard & Rich CLI**: Dark-mode moss forest dashboard with live drag-and-drop zone, Lucide icons, and real-time polling.

---

## 🏗️ Architecture

```
                                  [ User Drops Messy Files ]
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │  ~/SlothDen/Incoming │
                                   └──────────┬───────────┘
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │    SlothDesk Watcher Daemon      │
                             └────────────────┬─────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
          ┌──────────────────────┐                          ┌──────────────────────┐
          │  Text/Meta Extractor │                          │   1-Click Safety DB  │
          │ (PDF/Code/CSV/TXT/MD)│                          │      (SQLite)        │
          └──────────┬───────────┘                          └──────────┬───────────┘
                     │                                                 │
                     ▼                                                 │
      ┌──────────────────────────────┐                                 │
      │    Open-Source AI Engine     │                                 │
      │ ┌──────────────────────────┐ │                                 │
      │ │ Ollama (Llama 3.2 / Qwen)│ │                                 │
      │ ├──────────────────────────┤ │                                 │
      │ │ Embedded Local NLP Engine│ │                                 │
      │ └──────────────────────────┘ │                                 │
      └──────────────┬───────────────┘                                 │
                     │                                                 │
                     ▼                                                 ▼
      ┌──────────────────────────────┐                      ┌──────────────────────┐
      │  Autonomous File Organizer   │ ──(Logs Activity)──> │  Sloth Energy Meter  │
      │  • Semantic Categorization   │                      │  • Naps Earned 😴    │
      │  • ISO Standard Renaming     │                      │  • Minutes Saved ⏳  │
      │  • Sloth 1-Line TL;DR        │                      │  • $0 Cloud Spend 💰 │
      └──────────────┬───────────────┘                      └──────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ ~/SlothDen/Organized │
          │  ├── /finance/       │
          │  ├── /work/          │
          │  ├── /personal/      │
          │  ├── /code/          │
          │  └── /reading/       │
          └──────────────────────┘
```

---

## 🚀 Quick Start (60 Seconds)

### 1. Clone & Install
```bash
git clone https://github.com/your-username/slothdesk.git
cd slothdesk
pip install -r requirements.txt
```

### 2. Run the 10-Second Demo
Experience the full autonomous workflow instantly:
```bash
python run_demo.py
```
This script automatically drops realistic messy files (AWS bills, strategy sync notes, confidential medical results, code), wakes the sloth agent, organizes them into folders, calculates energy saved, runs a local RAG query, and demonstrates 1-click undo!

### 3. Launch the Cozy Web Dashboard
```bash
python sloth.py serve --port 8000
```
Open **`http://localhost:8000`** in your browser. Drag and drop any clutter, click **"Tidy Incoming Now"**, or ask questions in **"Ask My Clutter"**.

---

## 💻 CLI Commands

SlothDesk provides a full terminal suite with colorful Rich formatting:

```bash
# Tidy the incoming den immediately
python sloth.py tidy

# Run the sleepy background daemon (watches incoming directory continuously)
python sloth.py watch

# Check the Sloth Energy Meter (Naps earned, minutes saved, calories conserved)
python sloth.py stats

# Ask your local clutter a question in plain English (Local RAG)
python sloth.py ask "How much was my AWS bill?"

# Undo the last organization and restore the original filename & location
python sloth.py undo

# Launch the cozy Web UI
python sloth.py serve
```

---

## 🧠 Open-Source AI Core

SlothDesk is designed around **model flexibility and zero cloud lock-in**:

1. **Ollama / Local OpenAI Endpoint (Recommended for Maximum Intelligence)**:
   - Connects seamlessly to your local Ollama instance (`http://localhost:11434`).
   - Supports any open-weight model: `llama3.2:1b`, `llama3.2:3b`, `qwen2.5:0.5b`, `qwen2.5:7b`, `mistral:7b`, or `smollm2:360m`.
   - Set custom model: `export SLOTH_MODEL="qwen2.5:0.5b"`.

2. **Embedded Local Open NLP Engine (Zero Dependencies / Instant Fallback)**:
   - If Ollama is not running, SlothDesk automatically falls back to its built-in rule and semantic BM25/TF-IDF heuristics.
   - Runs in **under 5 milliseconds**, requires **0 MB of model downloads**, and guarantees that SlothDesk works out-of-the-box on literally any laptop on earth.

---

## 🔒 Why Open Innovation Matters

| Dimension | Closed Cloud API (OpenAI / Anthropic) | SlothDesk (Local Open-Source AI) |
|---|---|---|
| **Data Privacy** | Every bank statement, tax return, and medical slip is transmitted to remote servers. | **100% on-device.** No bytes ever leave your machine. |
| **Marginal Cost** | \$0.03–\$0.08 per document triage. A 1,000-file backlog costs \$50+. | **\$0.00.** Run it continuously for years at zero cost. |
| **Offline Reliability** | Fails on flights, trains, subways, or during internet dropouts. | **100% offline.** Works without internet connection. |
| **Longevity & Control** | Dependent on third-party pricing, rate limits, and API deprecations. | **Permanent ownership.** You control the weights and the code forever. |

---

## 🧪 Running Unit Tests

SlothDesk includes a comprehensive test suite with 100% passing tests:

```bash
python -m unittest discover -s tests
```

---

## 📜 License

MIT License. Feel free to use, modify, and be as lazy as you want. 🦥
