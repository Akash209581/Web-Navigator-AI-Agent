from core.listener import listen
from core.speaker import speak
from core.brain import ask_gpt  
from datetime import datetime
import subprocess
import os
import json
from dotenv import load_dotenv
from core.history import SessionStore
from core.browser import ThreadedBrowserSession
from typing import Protocol
import csv
from core.llm import LLMProvider

load_dotenv()
llm = LLMProvider()


def offline_reply(command):
    command = command.lower()

    if "your name" in command:
        return "I am Jarvis, your personal assistant."
    elif "who made you" in command:
        return "I was developed by my creator using Python."
    elif "how are you" in command:
        return "I'm functioning at full capacity!"
    elif "thank you" in command:
        return "You're welcome!"
    else:
        return "I'm sorry, I don't know how to handle that yet."


# Function to execute NirCmd commands
def execute_nircmd(command):
    path = "C:\\Program Files\\nircmd\\nircmd.exe"  # Update to your actual path
    try:
        if command == "unmute volume":
            subprocess.run([path, "mutesysvolume", "0"])
            return "Volume unmuted."
        elif command == "mute volume":
            subprocess.run([path, "mutesysvolume", "1"])
            return "Volume muted."
        elif command == "increase volume":
            subprocess.run([path, "changesysvolume", "9876"])  # ~10% up
            return "Volume increased."
        elif command == "volume down":
            subprocess.run([path, "changesysvolume", "-6553"])  # ~10% down
            return "Volume decreased."
        elif command == "shutdown":
            subprocess.run([path, "exitwin", "poweroff"])
            return "Shutting down the system."
        elif command == "restart":
            subprocess.run([path, "exitwin", "reboot"])
            return "Restarting the system."
        elif command == "log off":
            subprocess.run([path, "exitwin", "logoff"])
            return "Logging off."
        elif command == "open notepad":
            subprocess.run([path, "exec", "notepad.exe"])
            return "Opening Notepad."
        elif command == "open chrome":
            subprocess.run([path, "exec", "chrome.exe"])  # Ensure Chrome is in PATH or give full path
            return "Opening Chrome."
        elif command == "turn off monitor":
            subprocess.run([path, "monitor", "off"])
            return "Turning off the monitor."
        elif command.startswith("kill "):
            app = command.replace("kill ", "").strip()
            subprocess.run([path, "killprocess", f"{app}.exe"])
            return f"Killing process: {app}"
        else:
            return offline_reply(command)

    except Exception as e:
        return f"Error controlling volume: {e}"



# Function to query GPT for generating browser automation script
def ask_gpt_for_browser_script(command_text):
    """Use local-first LLM to produce a JSON array of browser actions."""
    try:
        return llm.plan_actions(command_text)
    except Exception:
        # Fallback minimal search plan
        return json.dumps([
            {"type": "goto", "url": "https://duckduckgo.com/"},
            {"type": "fill", "selector": "input[name='q']", "text": command_text},
            {"type": "press", "key": "Enter"},
            {"type": "wait", "duration": 3000},
        ])


# Handler to process commands with web navigation capability
def handle_browser_command(session, command):
    script_json = ask_gpt_for_browser_script(command)
    if not script_json or (isinstance(script_json, str) and script_json.startswith("ERROR_GPT_CALL")):
        # Fallback to offline heuristic if LLM failed
        try:
            lower = command.lower()
            if "search" in lower:
                query = lower.split("search", 1)[1].strip()
                if query.startswith("for "):
                    query = query[4:]
                fallback = [
                    {"type": "goto", "url": "https://duckduckgo.com/"},
                    {"type": "fill", "selector": "input[name='q']", "text": query or command},
                    {"type": "press", "key": "Enter"},
                    {"type": "wait", "duration": 3000},
                ]
            else:
                # open website/go to
                url = "https://www.google.com"
                for kw in ("open website", "go to"):
                    if kw in lower:
                        part = lower.split(kw, 1)[1].strip()
                        if part:
                            url = part.split()[0]
                            if not url.startswith("http"):
                                url = f"https://{url}"
                        break
                fallback = [
                    {"type": "goto", "url": url},
                    {"type": "wait", "duration": 1500},
                ]
            script_json = json.dumps(fallback)
        except Exception:
            return "Sorry, I am unable to fetch browser instructions right now."
    try:
        script = json.loads(script_json)
    except json.JSONDecodeError:
        return "Sorry, I couldn't understand the browser actions."
    return session.apply_script(script)


# ---------- New dynamic web navigator agent ----------
def gather_data_to_csv(items: list[dict], file_path: str) -> str:
    if not items:
        return "No data to save."
    keys = sorted({k for it in items for k in it.keys()})
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for it in items:
                writer.writerow({k: it.get(k, "") for k in keys})
        return f"Saved CSV: {file_path}"
    except Exception as e:
        return f"Failed to save CSV: {e}"


def web_navigator(session, store: SessionStore, session_id: str, user_cmd: str) -> str:
    """Handle dynamic browser tasks including search, click by text, coding playground flows, and data extraction."""
    text = user_cmd.lower()
    store.append_event(session_id, {"type": "user", "text": user_cmd})

    # Intent: top 5 laptops under X (Amazon-aware extraction if on Amazon)
    if ("laptops" in text and ("under" in text or "top" in text)) or text.startswith("search for laptops"):
        # Parse budget if present (supports numbers like 50000 or 50k)
        budget = None
        try:
            import re as _re
            m = _re.search(r"under\s*([\d,]+)\s*([kK]?)", text)
            if m:
                num = float(m.group(1).replace(",", ""))
                if m.group(2):
                    num *= 1000.0
                budget = num
            else:
                m2 = _re.search(r"under\s*(\d+)\s*[kK]", text)
                if m2:
                    budget = float(m2.group(1)) * 1000.0
        except Exception:
            budget = None

        # If not on amazon listing, search for it first
        page_info = session.summarize_page()
        url = (page_info or {}).get("url", "")
        if "amazon." not in url or "/s?" not in url:
            query = f"site:amazon.in laptops under {int(budget)}" if budget else user_cmd
            script = [
                {"type": "goto", "url": "https://duckduckgo.com/"},
                {"type": "fill", "selector": "input[name='q']", "text": query},
                {"type": "press", "key": "Enter"},
                {"type": "wait", "duration": 2500},
                {"type": "click_text", "text": "Amazon"},
                {"type": "wait", "duration": 2500},
            ]
            session.apply_script(script)

        # If we're on amazon listing now, use DOM extraction; else fallback to text heuristic
        items = []
        page_info = session.summarize_page()
        url = (page_info or {}).get("url", "")
        if "amazon." in url:
            items = session.extract_amazon_laptops_top_k(5, max_price=budget, currency="INR")
        if not items:
            items = session.extract_top_k_with_prices(5)

        # Save CSV when there's structured data
        csv_path = os.path.join(os.getcwd(), "laptops_top5.csv")
        _msg = gather_data_to_csv(items, csv_path) if items else "No data to save."
        store.append_event(session_id, {"type": "extraction", "items": items, "budget": budget, "csv": csv_path})
        return json.dumps({"query": user_cmd, "top5": items, "csv": csv_path}, ensure_ascii=False)

    # Intent: search something (use DDG by default)
    if text.startswith("search ") or text.startswith("search for "):
        query = text.split("search", 1)[1].strip()
        query = query[4:].strip() if query.startswith("for ") else query
        script = [
            {"type": "goto", "url": "https://duckduckgo.com/"},
            {"type": "fill", "selector": "input[name='q']", "text": query},
            {"type": "press", "key": "Enter"},
            {"type": "wait", "duration": 2000},
        ]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result})
        return result

    # Intent: learn current site profile (editor/run/output)
    if text.startswith("learn site") or text.startswith("profile site") or text.startswith("remember site"):
        script = [{"type": "learn_site"}]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "learn_site", "result": result})
        return "Learned site profile for this page."

    # Intent: click something by visible text
    if text.startswith("click ") or text.startswith("open "):
        target_text = user_cmd.split(" ", 1)[1] if " " in user_cmd else user_cmd
        script = [{"type": "click_text", "text": target_text}, {"type": "wait", "duration": 1500}]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result})
        return result

    # Intent: type code into an online compiler (generic)
    if text.startswith("select language ") or text.startswith("choose language "):
        lang = user_cmd.split(" ", 2)[2] if len(user_cmd.split(" ")) >= 3 else "python"
        # try to click a dropdown or text
        script = [
            {"type": "click_text", "text": lang},
            {"type": "wait", "duration": 800},
        ]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result})
        return result

    if (
        text.startswith("remove the existing code")
        or text.startswith("remove the code")
        or text.startswith("remove code")
        or text.startswith("clear code")
        or text.startswith("clear the code")
        or text.startswith("delete code")
        or text.startswith("erase code")
    ):
        script = [
            {"type": "focus_editor"},
            {"type": "clear_editor"},
        ]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result})
        return result

    if (
        text.startswith("write code ")
        or text.startswith("type code ")
        or text.startswith("write ")
        or text.startswith("type ")
        or text.endswith(" code")
    ):
        if text.startswith("write code "):
            prompt = user_cmd.partition("write code ")[2]
        elif text.startswith("type code "):
            prompt = user_cmd.partition("type code ")[2]
        elif text.startswith("write "):
            prompt = user_cmd.partition("write ")[2]
        elif text.startswith("type "):
            prompt = user_cmd.partition("type ")[2]
        else:
            # Handle trailing ' code' phrasing like 'addition of two numbers code'
            prompt = user_cmd[: -len(" code")]

        # If prompt looks like natural language, ask GPT to generate code.
        # Else treat it as literal code.
        def _looks_like_natural_language(s: str) -> bool:
            s2 = s.strip()
            return ("print(" not in s2 and "function" not in s2 and "def " not in s2 and "#include" not in s2 and "public static void main" not in s2)

        if _looks_like_natural_language(prompt):
            try:
                lang = session.detect_language()
                code = llm.generate_code(lang, prompt)
            except Exception:
                code = prompt
        else:
            code = prompt

        script = [
            {"type": "focus_editor"},
            # Type with a small delay so it looks like manual typing
            {"type": "write_code", "text": code, "delay": 12},
        ]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result, "generated": True})
        return result

    if (
        text.startswith("set code ")
        or text.startswith("rewrite code ")
        or text.startswith("replace code ")
        or text.startswith("over write code ")
        or text.startswith("overwrite code ")
        or text.startswith("remove the existing code and write ")
    ):
        if text.startswith("set code "):
            prompt = user_cmd.partition("set code ")[2]
        elif text.startswith("rewrite code "):
            prompt = user_cmd.partition("rewrite code ")[2]
        elif text.startswith("replace code "):
            prompt = user_cmd.partition("replace code ")[2]
        elif text.startswith("over write code "):
            prompt = user_cmd.partition("over write code ")[2]
        elif text.startswith("overwrite code "):
            prompt = user_cmd.partition("overwrite code ")[2]
        else:
            prompt = user_cmd.partition("remove the existing code and write ")[2]

        # Generate code via GPT if prompt looks like a natural-language spec
        if (";" not in prompt and "print(" not in prompt and "def " not in prompt):
            try:
                lang = session.detect_language()
                code = llm.generate_code(lang, prompt)
            except Exception:
                code = prompt
        else:
            code = prompt

        script = [
            {"type": "focus_editor"},
            # Slow-typing replace: clear then type with delay for a natural look
            {"type": "clear_editor"},
            {"type": "type_code", "text": code, "delay": 12},
        ]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result, "generated": True})
        return result

    if text.startswith("run code") or text.startswith("execute"):
        script = [
            {"type": "run_code"},
            {"type": "wait", "duration": 3000},
        ]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result})
        return result

    # Intent: get output after running code
    if text.startswith("get output") or text.startswith("read output") or text.startswith("show output"):
        script = [{"type": "get_output"}]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "action", "script": script, "result": result})
        return result

    if text.startswith("debug"):
        # naive: look for error text after run and attempt an auto-fix cycle if possible
        page_info = session.summarize_page()
        body = page_info.get("body", "")
        err_lines = [l for l in body.splitlines() if any(k in l.lower() for k in ("error", "traceback", "exception"))]
        msg = "\n".join(err_lines[:10]) or "No obvious error found."
        store.append_event(session_id, {"type": "debug", "info": msg})
        # Auto-rewrite suggestion: if syntax error detected, suggest a simple Python addition template
        if "syntax" in body.lower():
            fix_code = "a = 2\nb = 3\nprint(a + b)\n"
            script = [
                {"type": "set_code", "text": fix_code},
                {"type": "click_text", "text": "Run"},
                {"type": "wait", "duration": 2000},
            ]
            result = session.apply_script(script)
            store.append_event(session_id, {"type": "auto_fix", "script": script, "result": result})
            return f"Tried a quick fix and re-ran. Error summary was:\n{msg}"
        return msg

    # Intent: top 5 laptops under X (Amazon-aware extraction if on Amazon)
    if "laptops" in text and ("under" in text or "top" in text):
        # Parse budget if present (supports numbers like 50000 or 50k)
        budget = None
        try:
            import re as _re
            m = _re.search(r"under\s*([\d,]+)\s*([kK]?)", text)
            if m:
                num = float(m.group(1).replace(",", ""))
                if m.group(2):
                    num *= 1000.0
                budget = num
            else:
                m2 = _re.search(r"under\s*(\d+)\s*[kK]", text)
                if m2:
                    budget = float(m2.group(1)) * 1000.0
        except Exception:
            budget = None

        # If not on amazon listing, search for it first
        page_info = session.summarize_page()
        url = (page_info or {}).get("url", "")
        if "amazon." not in url or "/s?" not in url:
            query = f"site:amazon.in laptops under {int(budget)}" if budget else user_cmd
            script = [
                {"type": "goto", "url": "https://duckduckgo.com/"},
                {"type": "fill", "selector": "input[name='q']", "text": query},
                {"type": "press", "key": "Enter"},
                {"type": "wait", "duration": 2500},
                {"type": "click_text", "text": "Amazon"},
                {"type": "wait", "duration": 2500},
            ]
            session.apply_script(script)

        # If we're on amazon listing now, use DOM extraction; else fallback to text heuristic
        items = []
        page_info = session.summarize_page()
        url = (page_info or {}).get("url", "")
        if "amazon." in url:
            items = session.extract_amazon_laptops_top_k(5, max_price=budget, currency="INR")
        if not items:
            items = session.extract_top_k_with_prices(5)
        store.append_event(session_id, {"type": "extraction", "items": items, "budget": budget})
        return json.dumps({"query": user_cmd, "top5": items}, ensure_ascii=False)

    # Intent: gather data and save to csv
    if text.startswith("gather some data about "):
        topic = user_cmd.split("gather some data about ", 1)[1]
        script = [
            {"type": "goto", "url": "https://duckduckgo.com/"},
            {"type": "fill", "selector": "input[name='q']", "text": topic},
            {"type": "press", "key": "Enter"},
            {"type": "wait", "duration": 3000},
        ]
        session.apply_script(script)
        # Get some items from page
        page_info = session.summarize_page()
        items = []
        for l in page_info.get("links", [])[:50]:
            items.append({"text": l.get("text"), "href": l.get("href")})
        csv_path = os.path.join(os.getcwd(), "gathered_data.csv")
        msg = gather_data_to_csv(items, csv_path)
        store.append_event(session_id, {"type": "gather", "topic": topic, "csv": csv_path, "count": len(items)})
        return msg

    # Intent: extract tables and save to CSV
    if text.startswith("export tables") or text.startswith("extract tables"):
        script = [{"type": "extract_tables"}]
        _ = session.apply_script(script)
        # we stored table rows in the last action's value, but apply_script returns text only
        # call summarize and re-extract via separate helper: do another pass via page summary
        page_info = session.summarize_page()
        # Fallback quick table-like link export when no <table> exists
        items = []
        for l in page_info.get("links", [])[:100]:
            items.append({"text": l.get("text"), "href": l.get("href")})
        csv_path = os.path.join(os.getcwd(), "tables_or_links.csv")
        msg = gather_data_to_csv(items, csv_path)
        store.append_event(session_id, {"type": "export_csv", "path": csv_path, "count": len(items)})
        return msg

    # Intent: screenshot
    if text.startswith("screenshot"):
        path = os.path.join(os.getcwd(), "page.png")
        script = [{"type": "screenshot", "path": path}]
        result = session.apply_script(script)
        store.append_event(session_id, {"type": "screenshot", "path": path})
        return result

    # Default: treat like regular browser command
    script_result = handle_browser_command(session, user_cmd)
    store.append_event(session_id, {"type": "fallback", "cmd": user_cmd, "result": script_result})
    return script_result


def main():
    speak("Jarvis is now running. Say 'Jarvis' to wake me up.")
    store = SessionStore()
    browser_session = ThreadedBrowserSession()
    session_id = store.start_session({"app": "jarvis", "version": 1})

    while True:
        try:
            print("🎙 Listening for wake word...")
            wake_text = listen().lower()
            print(f"Wake word: {wake_text}")

            if "jarvis" in wake_text:
                speak("Yes? I’m listening.")

                while True:  # Active until "stop" or "sleep"
                    command = listen().lower()
                    print(f"🗣 You said: {command}")

                    if not command:
                        speak("Sorry, I didn’t catch that.")
                        continue

                    if "stop" in command or "sleep" in command:
                        speak("Okay, going to sleep. Call me if you need me.")
                        break

                    # System commands
                    elif "unmute volume" in command:
                        speak(execute_nircmd("unmute volume"))
                    elif "mute volume" in command:
                        speak(execute_nircmd("mute volume"))
                    elif "increase volume" in command or "volume up" in command:
                        speak(execute_nircmd("increase volume"))
                    elif "volume down" in command or "decrease volume" in command:
                        speak(execute_nircmd("volume down"))
                    elif "turn off monitor" in command:
                        speak(execute_nircmd("turn off monitor"))
                    elif "open chrome" in command:
                        speak(execute_nircmd("open chrome"))
                    elif "open notepad" in command:
                        speak(execute_nircmd("open notepad"))
                    elif "shutdown" in command:
                        speak(execute_nircmd("shutdown"))

                    # Time and Date
                    elif "time" in command:
                        now = datetime.now().strftime("%I:%M %p")
                        speak(f"The current time is {now}")
                    elif "date" in command:
                        today = datetime.now().strftime("%B %d, %Y")
                        speak(f"Today's date is {today}")

                    # Handle web navigation and dynamic tasks
                    elif (
                        "open website" in command
                        or "search" in command
                        or "go to" in command
                        or "click" in command
                        or "learn site" in command
                        or "profile site" in command
                        or "remember site" in command
                        or "select language" in command
                        or "choose language" in command
                        or "write code" in command
                        or command.startswith("write ")
                        or "type code" in command
                        or command.startswith("type ")
                        or "set code" in command
                        or "rewrite code" in command
                        or "replace code" in command
                        or "remove the existing code" in command
                        or "remove the code" in command
                        or "remove code" in command
                        or "clear code" in command
                        or "clear the code" in command
                        or "run code" in command
                        or "execute" in command
                        or "debug" in command
                        or "gather some data about" in command
                        or "laptops" in command
                    ):
                        response = web_navigator(browser_session, store, session_id, command)
                        speak(response)

                    # Offline voice replies
                    elif "your name" in command:
                        speak(offline_reply("your name"))
                    elif "who made you" in command:
                        speak(offline_reply("who made you"))
                    elif "how are you" in command:
                        speak(offline_reply("how are you"))
                    elif "thank you" in command:
                        speak(offline_reply("thank you"))

                    # Default fallback to GPT chat
                    else:
                        try:
                            ai_reply = ask_gpt(command)
                            speak(ai_reply)
                        except Exception as e:
                            print(f"GPT error: {e}")
                            speak("Sorry, I’m having trouble accessing AI features right now.")

        except KeyboardInterrupt:
            print("🛑 Exiting...")
            break

        except Exception as e:
            print(f"❗ Error in main loop: {e}")
            speak("Something went wrong. Restarting listener.")

    # Clean up browser resources on exit
    try:
        browser_session.close()
    except Exception:
        pass


if _name_ == "_main_":
    try:
        main()
    except Exception as e:
        print(f"❌ Error occurred: {e}")
