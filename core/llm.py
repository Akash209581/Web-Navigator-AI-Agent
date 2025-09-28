import os
import json
import subprocess
from typing import Any, Dict, List, Optional

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore


class LLMProvider:
    """
    Local-first LLM provider.

    Priority:
    1) Ollama (local) via REST API (http://127.0.0.1:11434 by default)
    2) OpenAI (if OPENAI_API_KEY is set)
    3) Heuristic/offline fallback
    """

    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        try:
            from openai import OpenAI  # type: ignore
            self._openai = OpenAI(api_key=self.openai_api_key) if self.openai_api_key else None
        except Exception:
            self._openai = None

    # ---------------- Ollama helpers ----------------
    def _ollama_available(self) -> bool:
        if requests is None:
            return False
        try:
            r = requests.get(self.ollama_url + "/api/tags", timeout=0.8)
            return r.status_code == 200
        except Exception:
            return False

    def _ollama_chat(self, messages: List[Dict[str, str]], json_mode: bool = False) -> Optional[str]:
        if not self._ollama_available():
            return None
        payload: Dict[str, Any] = {
            "model": self.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0},
        }
        if json_mode:
            payload["format"] = "json"
        try:
            if requests is None:
                return None
            r = requests.post(self.ollama_url + "/api/chat", json=payload, timeout=60)
            if r.status_code != 200:
                return None
            data = r.json()
            content = data.get("message", {}).get("content")
            return content
        except Exception:
            return None

    # ---------------- OpenAI fallback ----------------
    def _openai_chat(self, system: str, user: str) -> Optional[str]:
        if not self._openai:
            return None
        for model in ("gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"):
            try:
                resp = self._openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0,
                    max_tokens=800,
                )
                return (resp.choices[0].message.content or "").strip()
            except Exception:
                continue
        return None

    # ---------------- Public APIs ----------------
    def plan_actions(self, command_text: str) -> str:
        """Return a JSON array string of browser actions for the given natural language command."""
        system = (
            "You generate a JSON array of browser actions from a natural-language command. "
            "Only return the JSON array, nothing else. Allowed types: 'goto', 'fill', 'click', "
            "'click_text', 'press', 'wait', 'screenshot'. Use 'goto' with full URL starting with http(s). "
            "For search queries, prefer DuckDuckGo (https://duckduckgo.com/)."
        )
        user = f"Command: {command_text}\nOutput: JSON array of actions."

        # 1) Try Ollama (JSON mode)
        txt = self._ollama_chat([
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ], json_mode=True)
        if not txt:
            # Fallback: non-JSON mode and we'll extract JSON ourselves
            txt = self._ollama_chat([
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ], json_mode=False)

        if not txt:
            # 2) Try OpenAI
            txt = self._openai_chat(system, user)

        if txt:
            # Extract a JSON array from text
            s = txt.strip()
            l = s.find("[")
            r = s.rfind("]")
            if l != -1 and r != -1 and r > l:
                return s[l : r + 1]

        # 3) Heuristic offline plan
        lower = command_text.lower()
        if "search" in lower:
            q = lower.split("search", 1)[1].strip()
            if q.startswith("for "):
                q = q[4:]
            return json.dumps([
                {"type": "goto", "url": "https://duckduckgo.com/"},
                {"type": "fill", "selector": "input[name='q']", "text": q or command_text},
                {"type": "press", "key": "Enter"},
                {"type": "wait", "duration": 3000},
            ])
        # default: open a URL if present, else search everything
        url = "https://www.google.com"
        for kw in ("open website", "go to"):
            if kw in lower:
                part = lower.split(kw, 1)[1].strip()
                if part:
                    url = part.split()[0]
                    if not url.startswith("http"):
                        url = f"https://{url}"
                break
        return json.dumps([
            {"type": "goto", "url": url},
            {"type": "wait", "duration": 1500},
        ])

    def generate_code(self, language: str, prompt: str) -> str:
        """Return a minimal code snippet for the given language and prompt."""
        sys = (
            "You write minimal, self-contained code snippets. "
            "Return ONLY code without explanations."
        )
        usr = f"Write {language} code for: {prompt}. Keep it minimal."

        def _strip_code_fences(text: str) -> str:
            s = (text or "").strip()
            if "```" in s:
                parts = s.split("```")
                if len(parts) >= 3:
                    core = parts[1]
                    lines = core.splitlines()
                    if lines:
                        # Drop possible language tag on first line
                        first = lines[0].strip().lower()
                        if first in (language.lower(), language[:3].lower(), "python", "js", "javascript", "java", "c++", "c#", "typescript", "go", "ruby", "php"):
                            lines = lines[1:]
                    return "\n".join(lines).strip()
            return s

        # 1) Ollama chat API
        txt = self._ollama_chat([
            {"role": "system", "content": sys},
            {"role": "user", "content": usr},
        ], json_mode=False)
        if txt:
            code = _strip_code_fences(txt)
            if code:
                return code

        # 2) Ollama CLI fallback
        try:
            cmd = ["ollama", "run", self.ollama_model]
            full_prompt = f"{sys}\n\n{usr}"
            out = subprocess.run(cmd, input=full_prompt.encode("utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
            if out.returncode == 0:
                raw = out.stdout.decode("utf-8", errors="ignore")
                code = _strip_code_fences(raw)
                if code:
                    return code
        except Exception:
            pass

        # 3) OpenAI fallback
        txt = self._openai_chat(sys, usr)
        if txt:
            code = _strip_code_fences(txt)
            if code:
                return code

        # Offline default
        if language.lower().startswith("python"):
            return "print('Hello from Jarvis')\n"
        return "Hello from Jarvis\n"
