<div align="center">

# 🌐 Web Navigator Agent — OneCompiler 🚀

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Automation-45ba4b?logo=playwright&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-Ollama-8a2be2)

![Voice](https://img.shields.io/badge/Voice-PyAudio%20%7C%20SpeechRecognition-ff9800)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-4db33d?logo=mongodb&logoColor=white)
![OS](https://img.shields.io/badge/OS-Windows-0078D6?logo=windows&logoColor=white)

**HACXPB002 — Web Navigator AI Agent (OneCompiler)**

Build an AI agent that takes natural language instructions and autonomously drives the web on your local machine.

“Search for laptops under 50k and list top 5” → The agent plans, navigates, extracts clean JSON, and reads results out loud.

</div>

## Reason to Choose the Problem Statement
The current Era going to develop in the agentic ai, in this case as we develop this type of ai agents with enhanced featurers for the users we can easily grab the oppurtunity to be the number one in the current society and also this autonomous web navigation ai agent will help many peoples in the existing situations and do work easy,compatible.

## ✨ Highlights

- **Voice-first assistant** for browsing, research, data extraction, and coding-in-browser
- **Custom Online Compiler (React + JS):**
  - Auto-detects programming language after code is written (heuristic)
  - AI + Voice integration to generate/write code
  - One-click editor access for running code (JS runs in sandbox iframe)
-**Learn-site for understanding the whole website interface without getting errors with the wrong css selectors**
- Robust Playwright session with editor control (Monaco, CodeMirror, Ace, contenteditable, textarea)
- Structured outputs: JSON by default, CSV only for real HTML tables, screenshots when needed
- Session logging to MongoDB  and gives output as   JSON (guaranteed)
- Optional streaming API (“Web Erverywhere API”) with task/research/deep_research agents

## Tech Stack 
- Frontend : react with javascript
- orchestration: python
- Browser Automation : playwright
- LLm : ollama (local)
- database(session logging) : mongodb

## Proposed Approach (2–3 lines)

- User gives a natural language command.
- Ollama LLM running locally interprets and plans browser tasks.
- Browser automation executes these tasks (search, click, extract).
- Relevant data is extracted and formatted as structured output (e.g., JSON, CSV).


## 🧠 implementaion plan

Natural language input  → Local-first LLM ollma for intent & planning → Playwright automation → DOM extraction → Clean JSON/CSV → Voice summary.

## Scalability Considerations 
- Reliability: thread-isolated Playwright, consent/CAPTCHA cues, resilient selectors
- Quality of output: budget filters, JSON saved to files, CSV only for true tables
- Generality: works for laptops, products, tables, and generic “gather details …” research
- Extensibility: API server, modular browser session, easy to add new sites/extractors

## 🏗️ Architecture

- `main.py`: Voice loop, intents, GPT fallback, dynamic Amazon flow (fuzzy + product-page price)
- `core/browser.py`: All Playwright actions, editor helpers, Amazon extractors, table extractor
- `core/site_profile.py`: Learns run/output controls on coding sites
- `core/history.py`: Dual-write session logs (MongoDB+file), robust file fallback
- `web_api.py`: Experimental FastAPI server for streaming agents (task/research/deep)
- `web_erverywhere_agents.py`: Agent wiring (re-export for future renames)
- `ai-code-browser`: contains the frontend,backend of the compiler 

## 🔑 Capabilities

- Voice I/O: wake word, continuous listening, TTS responses
-Navigation: open/search/click, scroll, screenshots, site learning
- Editors: focus, set/clear, human-like typing, run, get output4
- - **Custom Compiler (React):**
  - Auto language detection (heuristic keywords)
  - AI-powered code writing via voice (hooks provided for LLM)
  - Run JS code in integrated sandbox iframe; other languages show reproducible file export
- Fuzzy matching: “iphone 14” → matches “Apple iPhone 14 (256 GB) …” and opens product page
- Price extraction: reads canonical price selectors on product page for accuracy
- Research: “gather the details of …” → searches, opens top links, collects snippets, saves JSON
- CSV export: only for real HTML tables (“export tables”) or data extraction 

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
`examples`
- `laptops_top5_YYYYMMDD_HHMMSS.json`
- `amazon_results_<query>_YYYYMMDD_HHMMSS.json`
- `gather_<topic>_YYYYMMDD_HHMMSS.json`
- `exported_table_*.csv` (only when extracting real HTML tables)

## 🗣️ Voice Command Cheat‑Sheet

- Open/search: “open website example.com”, “search for python list comprehensions”
- Learn/write/clear: “learn site”, “clear code”, “write code print hello”
- Run/read: “run code”, “get output”
- Data: “laptops under 50k”, “export tables”, “gather the details of …”
- Amazon: “search <product> on amazon”, “price of <product> on amazon”

## Contribution

- Akash – Developed the custom compiler( implemented features like detects automatically changes compiler accoding to code) frontend and implemented parts of the backend, 
- Maruthi – Implemented agent orchestration and refined voice command handling for smooth interaction.
- Varshitha – Enhanced core components, integrated them with main.py, and managed session history with database persistence.
- AbhiRam – Refined the browser tasking module, improving the agent’s ability to perform complex real-world tasks.
- Daniel – Contributed to browser automation using Playwright, worked on core components, and assisted with backend development of the compiler.

## 🧪 Troubleshooting

- Mic not picked up → check Windows recording device & install `pyaudio` via `pipwin`
- Playwright missing browsers → `python -m playwright install chromium`
- CAPTCHA pages → Solve manually; the agent will continue
- Paths with spaces (PowerShell) → always quote executable paths



---

Made with ❤️ for OneCompiler and HacXLerate. 
