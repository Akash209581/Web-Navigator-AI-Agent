<div align="center">

# 🌐 Web Navigator Agent — OneCompiler Hackathon 🚀

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b?logo=playwright&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009485?logo=fastapi&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Ollama%20%7C%20OpenAI-8a2be2)
![Voice](https://img.shields.io/badge/Voice-PyAudio%20%7C%20SpeechRecognition-ff9800)
![MongoDB](https://img.shields.io/badge/MongoDB-Optional-4db33d?logo=mongodb&logoColor=white)
![OS](https://img.shields.io/badge/OS-Windows-0078D6?logo=windows&logoColor=white)

**HACXPB002 — Web Navigator AI Agent (OneCompiler Hackathon)**

Build an AI agent that takes natural language instructions and autonomously drives the web on your local machine.

“Search for laptops under 50k and list top 5” → The agent plans, navigates, extracts clean JSON, and reads results out loud.

</div>

## ✨ Highlights

- Voice-first assistant for browsing, research, data extraction, and coding-in-browser
- Robust Playwright session with editor control (Monaco, CodeMirror, Ace, contenteditable, textarea)
- Amazon-aware extraction with “blind rule” (skip top 3 ads/labels), sponsored skip, and fuzzy matching
- Product-page price extractor for accurate “price of X on Amazon” answers
- Structured outputs: JSON by default, CSV only for real HTML tables, screenshots when needed
- Session logging to MongoDB (optional) and always to JSONL (guaranteed)
- Optional streaming API (“Web Erverywhere API”) with task/research/deep_research agents

## 🧠 Problem → Approach

Natural language in → Local-first LLM for intent & planning → Playwright automation → DOM extraction → Clean JSON/CSV → Voice summary.

Key differentiators for judges:
- Reliability: thread-isolated Playwright, consent/CAPTCHA cues, resilient selectors
- Quality of output: budget filters, JSON saved to files, CSV only for true tables
- Generality: works for laptops, products, tables, and generic “gather details …” research
- Extensibility: API server, modular browser session, easy to add new sites/extractors

## 🏗️ Architecture

- `main.py`: Voice loop, intents, GPT fallback, dynamic Amazon flow (fuzzy + product-page price)
- `core/browser.py`: All Playwright actions, editor helpers, Amazon extractors, table extractor
- `core/site_profile.py`: Learns run/output controls on coding sites
- `core/history.py`: Dual-write session logs (MongoDB+file), robust file fallback
- `webrover_api.py`: Experimental FastAPI server for streaming agents (task/research/deep)
- `web_erverywhere_agents.py`: Agent wiring (re-export for future renames)

## 🔑 Capabilities

- Voice I/O: wake word, continuous listening, TTS responses
- Navigation: open/search/click, scroll, screenshots, site learning
- Editors: focus, set/clear, human-like typing, run, get output
- Amazon: top-k products, blind rule (skip first 3), sponsored skip, product-link filter (/dp/, /gp/)
- Fuzzy matching: “iphone 14” → matches “Apple iPhone 14 (256 GB) …” and opens product page
- Price extraction: reads canonical price selectors on product page for accuracy
- Research: “gather the details of …” → searches, opens top links, collects snippets, saves JSON
- CSV export: only for real HTML tables (“export tables”)

## ⚙️ Setup (Windows + PowerShell)

Prerequisites:
- Python 3.12, Google Chrome, microphone enabled in Windows

Create env and install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
```

Environment (optional):

```powershell
Copy-Item .env.example .env
notepad .env
# OPENAI_API_KEY=sk-...
# MONGO_URI=mongodb://localhost:27017
```

## ▶️ Run (Voice Jarvis)

```powershell
python main.py
```

Say “Jarvis” to wake it up, then try:
- “search for laptops under 50000”
- “what is the price of iPhone 14 on amazon”
- “gather the details of last gst decrease”
- “learn site” → then “write code add two numbers” → “run code” → “get output”

Output files (auto-saved in project folder):
- `laptops_top5_YYYYMMDD_HHMMSS.json`
- `amazon_results_<query>_YYYYMMDD_HHMMSS.json`
- `gather_<topic>_YYYYMMDD_HHMMSS.json`
- `exported_table_*.csv` (only when extracting real HTML tables)

## 🌐 Optional: Streaming API (Web Erverywhere API)

1) Start Chrome with remote debugging (close all Chrome first):

```powershell
& "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --no-first-run --no-default-browser-check --start-maximized
```

2) Run the server:

```powershell
python webrover_api.py
```

3) Use endpoints:
- `POST /setup-browser` → `{ "url": "https://www.google.com" }`
- `POST /query` (SSE) → `{ "query": "best laptops 2025", "agent_type": "research" }`

## 🗣️ Voice Command Cheat‑Sheet

- Open/search: “open website example.com”, “search for python list comprehensions”
- Learn/write/clear: “learn site”, “clear code”, “write code print hello”
- Run/read: “run code”, “get output”
- Data: “laptops under 50k”, “export tables”, “gather the details of …”
- Amazon: “search <product> on amazon”, “price of <product> on amazon”

## 🧪 Troubleshooting

- Mic not picked up → check Windows recording device & install `pyaudio` via `pipwin`
- Playwright missing browsers → `python -m playwright install chromium`
- CAPTCHA pages → Solve manually; the agent will continue
- Paths with spaces (PowerShell) → always quote executable paths

## �️ Roadmap

- Site‑specific extractors for more marketplaces (Flipkart, eBay)
- Stronger PDF ingestion for research mode
- Agent auth and rate‑limit handling
- CI smoke tests for key flows

---

Made with ❤️ for the OneCompiler Hackathon. Impress judges by running a live demo: voice → plan → browse → extract → JSON/CSV/save.
