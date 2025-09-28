🌐 Web-Navigator-Agent-One-Compiler 🚀
📝 Problem Statement Chosen

HACXPB002 - Web Navigator AI Agent (OneCompiler Hackathon):
Build an AI Agent that can take natural language instructions and autonomously drive the web on a local computer.

👉 Example: "search for laptops under 50k and list top 5"

The system must combine a locally running LLM (for understanding and planning) with browser automation (like Playwright or Chrome Headless).

💡 Detailed Proposal & Prototype Plan

We aim to create an autonomous research and coding agent that:

Interprets natural language instructions 🎙️

Plans & executes browser navigation 🖥️

Extracts structured information 📊

(Optionally) writes & executes code inside online editors 💻

The result is a Research + Code + Execute workflow powered by voice, AI, and automation.

🛠️ Prototype Plan
🔎 Instruction Parsing

Accept natural language commands via voice or text

Use a local LLM (Ollama / GPT) for intent detection & planning

🌍 Web Automation

Use Playwright with a controlled Chrome session

Navigate sites, click, scroll, solve CAPTCHAs (manual fallback)

📑 Result Extraction

Extract lists, tables, text, prices, and code snippets

Handle special cases (e.g., Amazon laptops with price filter)

🎯 Result Presentation

Output in structured JSON / CSV

Summaries and optional text-to-speech playback

⚡ Integration

CLI interface + optional lightweight Flask/FastAPI frontend

Streamed updates for research tasks

✨ Features to Be Implemented

✅ Natural language commands (voice + text)
✅ Local LLM-powered parsing with intent detection
✅ Autonomous web navigation (multi-step, multi-page)
✅ Editor support: Monaco, CodeMirror, Ace, contenteditable, textarea
✅ Data extraction & cleaning (tables, lists, prices, code outputs)
✅ Structured outputs → JSON, CSV, screenshots
✅ GPT-assisted code writing with slow typing animation
✅ Error handling & CAPTCHA support
✅ Session logging → MongoDB or JSONL

🧰 Tech Stack Used

Programming Language: 🐍 Python (primary)

Orchestration & Logic: LangChain / custom logic

Local LLM Host: 🦙 Ollama (with fallback to OpenAI API)

Browser Automation: 🎭 Playwright

Data Extraction: BeautifulSoup + Playwright selectors

Voice I/O: 🎤 SpeechRecognition, PyAudio, pyttsx3

UI/Interface: CLI + optional 🌐 Flask/FastAPI web UI

Database (optional): 🗄️ MongoDB (or JSONL fallback)

Version Control: Git + GitHub

👥 Collaborators & Team Members

📌 Work Split Among 5 Members:

Maruthi→ Voice I/O (wake word, speech recognition, text-to-speech)

Varshi → Browser automation (Playwright setup, navigation, editor actions)

Abhi → Data extraction (Amazon laptops, tables, JSON/CSV export)

Daniel → Backend API & integration (FastAPI/Flask, SSE streaming, MongoDB logging)

Akash→ UI/CLI & overall testing (command interface, error handling, documentation)
