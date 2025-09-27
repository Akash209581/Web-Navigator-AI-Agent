# Web-Navigator-Agent-One-Compiler
# Problem Statement Chosen
HACXPB002 - Web Navigator AI Agent (OneCompiler Hackathon):
Build an AI Agent that can take natural language instructions and autonomously drive the web on a local computer. The system should combine a locally running LLM (for understanding and planning) with browser automation such as Chrome Headless or a browser in a local VM. Example use: "search for laptops under 50k and list top 5".

# Detailed Proposal & Prototype Plan Proposal
We aim to develop an autonomous agent that interprets user instructions, plans web navigation, controls a browser headlessly, extracts relevant information, and returns structured results. The agent merges natural language understanding with browser automation to create a unique Research + Code + Execute workflow.

# Prototype Plan
Instruction Parsing: Accept natural language instructions and use a local LLM to convert them into actionable steps.

Web Automation: Use Playwright to open a browser, interact with elements, and navigate websites.

Result Extraction: Scrape relevant data (lists, text, tables) as defined by parsed instructions.

Result Presentation: Compile results in a user-friendly structured format and (optionally) execute any extracted code using the OneCompiler API.

Integration: Provide a simple UI/CLI to submit queries and view results.

# Features to Be Implemented
Natural language command input

Local LLM-based instruction parsing & intent detection

Autonomous web navigation (multi-step, multi-page)

Data extraction & cleaning (tables, lists, code snippets)

Structured output generation (JSON,csv)

Basic error handling and recovery for dynamic web pages

Modular design for easy feature expansions

# Tech Stack Used
Programming Language: Python (primary) or Node.js (optional)

Orchestration & Logic: LangChain or custom Python logic

Local LLM Host: Ollama 

Browser Automation: Playwright 

Data Extraction: BeautifulSoup (Python) 

UI/Interface: CLI and/or minimal web frontend (Flask)

Version Control: Git, GitHub for collaboration

