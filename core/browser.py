from __future__ import annotations
import os
import re
import json
from typing import Any, Dict, List, Optional, Tuple
from playwright.sync_api import sync_playwright, Page, Browser
from .site_profile import SiteProfile
from concurrent.futures import ThreadPoolExecutor


class BrowserSession:
    def __init__(self):
        self._p = None
        self._browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self._profile: Optional[SiteProfile] = None

    def ensure_open(self):
        if self._p is None:
            self._p = sync_playwright().start()
        if self._browser is None:
            self._browser = self._p.chromium.launch(headless=False)
        if self.page is None:
            self.page = self._browser.new_page()
        return self.page

    def close(self):
        try:
            if self._browser:
                self._browser.close()
        finally:
            self._browser = None
            self.page = None
            if self._p is not None:
                try:
                    self._p.stop()
                except Exception:
                    pass
                self._p = None

    # ---------- helpers ----------
    def _handle_google_consent(self, page: Page):
        try:
            selectors = [
                "button:has-text('I agree')",
                "button:has-text('Accept all')",
                "button:has-text('Accept')",
                "//button[.='I agree']",
                "//button[.='Accept all']",
            ]
            for sel in selectors:
                try:
                    page.locator(sel).first.wait_for(state="visible", timeout=1500)
                    page.locator(sel).first.click()
                    break
                except Exception:
                    continue
        except Exception:
            pass

    def _captcha_present(self, page: Page) -> bool:
        try:
            text_signals = [
                r"text=/I'm not a robot/i",
                r"text=/unusual traffic/i",
                r"text=/verify you are human/i",
                r"text=/complete a quick verification/i",
                r"text=/Press & hold/i",
            ]
            for t in text_signals:
                if page.locator(t).count() > 0:
                    return True
            sels = [
                "iframe[title*='reCAPTCHA']",
                "iframe[src*='recaptcha']",
                "iframe[src*='challenges']",
                "#g-recaptcha",
                ".hcaptcha-box",
            ]
            for s in sels:
                if page.locator(s).count() > 0:
                    return True
        except Exception:
            pass
        return False

    def _wait_out_captcha(self, page: Page, max_ms=180000) -> bool:
        waited = 0
        step = 1000
        did_wait = False
        while self._captcha_present(page) and waited < max_ms:
            did_wait = True
            page.wait_for_timeout(step)
            waited += step
        return did_wait and not self._captcha_present(page)

    def _smart_fill(self, page: Page, selector: Optional[str], text: str) -> bool:
        candidates = [selector] if selector else []
        normalized = selector.replace('"', "'") if selector else ""
        if normalized in ("input[name='q']", "input[name=q]"):
            candidates += ["textarea[name='q']", "#APjFqb"]
        # DDG
        candidates += ["input[name='q']"]
        for sel in [c for c in candidates if c]:
            try:
                page.locator(sel).first.wait_for(state="visible", timeout=4000)
                page.fill(sel, text)
                return True
            except Exception:
                continue
        try:
            page.keyboard.type(text)
            return True
        except Exception:
            return False

    # ---------- editor helpers ----------
    def _focus_editor(self, page: Page) -> bool:
        candidates = [
            ".monaco-editor .view-lines",
            ".CodeMirror",
            ".cm-content",
            ".cm-editor",
            ".ace_editor",
            "[contenteditable='true']",
            "textarea",
        ]
        for sel in candidates:
            try:
                loc = page.locator(sel).first
                if loc.count() > 0:
                    # For hidden inputs like Ace's textarea, click the visible container
                    if sel == "textarea" and loc.get_attribute('class') and 'ace_text-input' in (loc.get_attribute('class') or ''):
                        try:
                            page.locator('.ace_editor').first.click()
                        except Exception:
                            pass
                    else:
                        loc.click()
                    return True
            except Exception:
                continue
        return False

    def _set_textarea_value(self, page: Page, text: str) -> bool:
        try:
            # Prefer the largest textarea (by rows/cols/size)
            textareas = page.locator('textarea')
            if textareas.count() > 0:
                # Use first for simplicity; many editors have only one
                return bool(page.eval_on_selector(
                    'textarea',
                    "(el, t) => { el.value = t; el.dispatchEvent(new Event('input', {bubbles:true})); return true; }",
                    text,
                ))
        except Exception:
            pass
        return False

    def _set_monaco_value(self, page: Page, text: str) -> bool:
        try:
            return bool(page.evaluate("""
                (t) => {
                  if (window.monaco && monaco.editor) {
                    const models = monaco.editor.getModels();
                    if (models && models.length) { models[0].setValue(t); return true; }
                  }
                  // Some sites attach editor instance to window.editor
                  if (window.editor && typeof window.editor.setValue === 'function') {
                    window.editor.setValue(t); return true;
                  }
                  return false;
                }
            """, text))
        except Exception:
            return False

    def _set_codemirror_value(self, page: Page, text: str) -> bool:
        # CodeMirror 5
        try:
            ok = page.evaluate("""
                (t) => {
                  const cmEl = document.querySelector('.CodeMirror');
                  if (cmEl && cmEl.CodeMirror) { cmEl.CodeMirror.setValue(t); return true; }
                  return false;
                }
            """, text)
            if ok:
                return True
        except Exception:
            pass
        # CodeMirror 6
        try:
            ok = page.evaluate("""
                (t) => {
                  const root = document.querySelector('.cm-editor');
                  if (!root) return false;
                  const view = root.cmView || root.view || root.__cmView || root.editorView || (root.cm && root.cm.view) || null;
                  if (view && view.state) {
                    view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: t } });
                    return true;
                  }
                  // fallback to contenteditable area
                  const editable = root.querySelector('.cm-content[contenteditable="true"]') || document.querySelector('.cm-content[contenteditable="true"]');
                  if (editable) {
                    editable.innerText = t;
                    editable.dispatchEvent(new InputEvent('input', { bubbles: true }));
                    return true;
                  }
                  return false;
                }
            """, text)
            if ok:
                return True
        except Exception:
            pass
        return False

    def _set_ace_value(self, page: Page, text: str) -> bool:
        try:
            ok = page.evaluate("""
                (t) => {
                  const aceEl = document.querySelector('.ace_editor');
                  if (!aceEl) return false;
                  const e = aceEl.env && aceEl.env.editor ? aceEl.env.editor : (window.ace && window.ace.edit ? window.ace.edit(aceEl) : null);
                  if (e && e.session && typeof e.setValue === 'function') {
                    e.setValue(t, -1);
                    return true;
                  }
                  return false;
                }
            """, text)
            return bool(ok)
        except Exception:
            return False

    def _set_contenteditable_value(self, page: Page, text: str) -> bool:
        try:
            ok = page.evaluate("""
                (t) => {
                  const el = document.querySelector('[contenteditable="true"]');
                  if (!el) return false;
                  el.innerText = t;
                  el.dispatchEvent(new InputEvent('input', { bubbles: true }));
                  return true;
                }
            """, text)
            return bool(ok)
        except Exception:
            return False

    def clear_editor(self) -> bool:
        p = self.ensure_open()
        # Try programmatic clears first
        cleared = False
        try:
            if self._set_monaco_value(p, ""):
                cleared = True
            elif self._set_codemirror_value(p, ""):
                cleared = True
            elif self._set_ace_value(p, ""):
                cleared = True
            elif self._set_textarea_value(p, ""):
                cleared = True
            elif self._set_contenteditable_value(p, ""):
                cleared = True
        except Exception:
            pass
        if cleared:
            return True
        # Fallback: focus and select-all delete
        ok = self._focus_editor(p)
        try:
            p.keyboard.press('Control+A')
            p.keyboard.press('Delete')
            return True
        except Exception:
            return ok

    def type_code(self, text: str, delay_ms: int = 0) -> bool:
        p = self.ensure_open()
        self._focus_editor(p)
        try:
            # Use built-in typing with optional per-character delay
            p.keyboard.type(text, delay=delay_ms)
            return True
        except Exception:
            return False

    def set_code(self, text: str) -> bool:
        p = self.ensure_open()
        # Try targeted programmatic updates for common editors
        try:
            if self._set_monaco_value(p, text):
                return True
            if self._set_codemirror_value(p, text):
                return True
            if self._set_ace_value(p, text):
                return True
            if self._set_textarea_value(p, text):
                return True
            if self._set_contenteditable_value(p, text):
                return True
        except Exception:
            pass
        # Fallback: clear then type
        ok = self.clear_editor()
        typed = self.type_code(text)
        return ok or typed

    def _auto_find_and_focus_editor(self, page: Page) -> bool:
        # Scroll through the page and try to focus an editor-like element
        for y in range(0, 4000, 400):
            try:
                page.mouse.wheel(0, 400)
            except Exception:
                pass
            if self._focus_editor(page):
                return True
        # Try back to top and second pass
        try:
            page.evaluate("window.scrollTo(0,0)")
        except Exception:
            pass
        for y in range(0, 4000, 400):
            try:
                page.mouse.wheel(0, 400)
            except Exception:
                pass
            if self._focus_editor(page):
                return True
        return False

    def get_code(self) -> str:
        p = self.ensure_open()
        # Try textarea value
        try:
            val = p.eval_on_selector("textarea", "e => e && e.value")
            if val:
                return str(val)
        except Exception:
            pass
        # Try CodeMirror content
        try:
            if p.locator('.cm-content').count() > 0:
                return p.locator('.cm-content').inner_text()
        except Exception:
            pass
        # Try Monaco lines
        try:
            if p.locator('.monaco-editor .view-lines').count() > 0:
                return p.locator('.monaco-editor .view-lines').inner_text()
        except Exception:
            pass
        # Fallback body
        try:
            return p.locator('body').inner_text()
        except Exception:
            return ""

    # ---------- public API ----------
    def summarize_page(self, max_links: int = 30, max_chars: int = 3000) -> Dict[str, Any]:
        p = self.ensure_open()
        url = p.url
        title = p.title()
        # Collect some clickable texts
        links = []
        try:
            for l in p.locator("a").all()[:max_links]:
                try:
                    t = l.inner_text().strip()
                    href = l.get_attribute("href")
                    if t or href:
                        links.append({"text": t[:200], "href": href})
                except Exception:
                    continue
        except Exception:
            pass
        # Visible body text (truncate)
        body_text = ""
        try:
            body_text = p.locator("body").inner_text()[:max_chars]
        except Exception:
            pass
        return {"url": url, "title": title, "links": links, "body": body_text}

    def apply_script(self, script: List[Dict[str, Any]]) -> str:
        p = self.ensure_open()
        try:
            error_msg = None
            for action in script:
                atype = action.get("type")
                if atype == "goto":
                    url = action.get("url") or "about:blank"
                    p.goto(str(url), wait_until="domcontentloaded")
                    if "google." in p.url:
                        self._handle_google_consent(p)
                    if self._captcha_present(p):
                        solved = self._wait_out_captcha(p)
                        if not solved:
                            return "CAPTCHA detected. Please solve it in the browser and try again."
                elif atype == "click":
                    sel = action.get("selector")
                    if sel:
                        p.locator(sel).first.wait_for(state="visible", timeout=5000)
                        p.click(sel)
                elif atype == "click_text":
                    text = action.get("text")
                    if text:
                        p.get_by_text(text, exact=False).first.click()
                elif atype == "fill":
                    self._smart_fill(p, action.get("selector"), action.get("text", ""))
                elif atype == "type":
                    p.keyboard.type(action.get("text", ""))
                elif atype == "type_code":
                    ok = self.type_code(action.get("text", ""), delay_ms=int(action.get("delay", 0)))
                    if not ok:
                        error_msg = error_msg or "Couldn't type into the editor."
                elif atype == "clear_editor":
                    ok = self.clear_editor()
                    if not ok:
                        error_msg = error_msg or "Couldn't find an editor to clear on this page."
                elif atype == "set_code":
                    ok = self.set_code(action.get("text", ""))
                    if not ok:
                        error_msg = error_msg or "Couldn't find an editor to set code on this page."
                elif atype == "press":
                    key = action.get("key", "Enter")
                    sel = action.get("selector")
                    try:
                        if sel:
                            p.locator(sel).first.wait_for(state="visible", timeout=3000)
                            p.press(sel, key)
                        else:
                            p.keyboard.press(key)
                    except Exception:
                        p.keyboard.press(key)
                elif atype == "wait":
                    p.wait_for_timeout(action.get("duration", 1000))
                elif atype == "hover":
                    sel = action.get("selector")
                    if sel:
                        p.locator(sel).first.hover()
                elif atype == "scroll":
                    p.mouse.wheel(0, action.get("deltaY", 800))
                elif atype == "screenshot":
                    p.screenshot(path=action.get("path", "screenshot.png"))
                elif atype == "learn_site":
                    self._profile = SiteProfile.infer(p)
                elif atype == "focus_editor":
                    ok = self._auto_find_and_focus_editor(p)
                    if not ok:
                        error_msg = error_msg or "Couldn't find an editor on this page."
                elif atype == "write_code":
                    # Prefer manual typing effect if 'delay' provided, else try set_code first
                    text = action.get("text", "")
                    delay = int(action.get("delay", 0))
                    if delay > 0:
                        try:
                            self._auto_find_and_focus_editor(p)
                            ok = self.type_code(text, delay_ms=delay)
                            if not ok:
                                raise Exception("type failed")
                        except Exception:
                            # fallback to programmatic set
                            ok = self.set_code(text)
                            if not ok:
                                error_msg = error_msg or "Couldn't type or set code into the editor."
                    else:
                        ok = False
                        try:
                            ok = self.set_code(text)
                        except Exception:
                            ok = False
                        if not ok:
                            try:
                                self._auto_find_and_focus_editor(p)
                                ok2 = self.type_code(text)
                                if not ok2:
                                    error_msg = error_msg or "Couldn't type or set code into the editor."
                            except Exception:
                                pass
                elif atype == "run_code":
                    # Use learned profile if available
                    used = False
                    if self._profile:
                        if self._profile.run_selector:
                            try:
                                p.locator(self._profile.run_selector).first.click()
                                used = True
                            except Exception:
                                used = False
                        if not used:
                            for txt in self._profile.run_texts:
                                try:
                                    p.get_by_text(txt, exact=False).first.click()
                                    used = True
                                    break
                                except Exception:
                                    continue
                    if not used:
                        # Generic fallbacks
                        for txt in ["Run", "Run Code", "Execute", "Compile", "▶", "Play", "Submit", "Start"]:
                            try:
                                p.get_by_text(txt, exact=False).first.click()
                                used = True
                                break
                            except Exception:
                                continue
                        if not used:
                            for sel in ["button.run", "#run", ".run-btn", "[aria-label='Run']"]:
                                try:
                                    p.locator(sel).first.click()
                                    used = True
                                    break
                                except Exception:
                                    continue
                elif atype == "get_output":
                    # Return output text via value field in result
                    out_text = ""
                    if self._profile:
                        for sel in self._profile.output_selectors:
                            try:
                                if p.locator(sel).count() > 0:
                                    out_text = p.locator(sel).first.inner_text()
                                    break
                            except Exception:
                                continue
                    if not out_text:
                        for sel in [
                            ".output", "#output", "pre.output", "pre", ".terminal", ".console",
                            "#console", ".result", "#result", "textarea[readonly]", ".output-window"
                        ]:
                            try:
                                if p.locator(sel).count() > 0:
                                    out_text = p.locator(sel).first.inner_text()
                                    break
                            except Exception:
                                continue
                    action["value"] = out_text
                elif atype == "extract_tables":
                    # Extract visible HTML tables into list of rows
                    try:
                        tables = p.locator('table')
                        n = min(tables.count(), 10)
                        extracted = []
                        for i in range(n):
                            try:
                                table = tables.nth(i)
                                rows = table.locator('tr')
                                row_count = min(rows.count(), 200)
                                for r in range(row_count):
                                    cells = rows.nth(r).locator('th,td')
                                    cols = min(cells.count(), 50)
                                    extracted.append([cells.nth(c).inner_text() for c in range(cols)])
                            except Exception:
                                continue
                        action["value"] = extracted
                    except Exception:
                        action["value"] = []
            return error_msg or "I have completed the browsing task."
        except Exception as e:
            return f"Error during browser automation: {e}"

    # ---------- language heuristics ----------
    def detect_language(self) -> str:
        p = self.ensure_open()
        try:
            title = (p.title() or "").lower()
        except Exception:
            title = ""
        try:
            body = (p.locator('body').inner_text() or "").lower()
        except Exception:
            body = ""
        text = f"{title}\n{body}"
        url = (p.url or "").lower()
        # simple heuristics
        checks = [
            ("python", ["python", "print(", "def ", "pip "]),
            ("javascript", ["javascript", "js", "console.log", "node.js", ".js"]),
            ("java", ["java", "public static void main", ".java"]),
            ("c++", ["c++", "cpp", "#include <iostream>", ".cpp"]),
            ("c#", ["c#", ".cs", "using system;"]),
            ("typescript", ["typescript", "ts", ".ts"]),
            ("go", ["golang", "go ", "package main"]),
            ("php", ["php", "<?php"]),
            ("ruby", ["ruby", "puts "]),
        ]
        for lang, needles in checks:
            for n in needles:
                if n in text or n in url:
                    return lang
        return "python"

    def extract_text(self) -> str:
        p = self.ensure_open()
        try:
            return p.locator("body").inner_text()
        except Exception:
            return ""

    def extract_top_k_with_prices(self, k: int = 5) -> List[Dict[str, Any]]:
        text = self.extract_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        items: List[Tuple[str, Optional[str]]] = []
        price_re = re.compile(r"(₹\s?\d[\d,]*|\$\s?\d[\d,]*|Rs\.?\s?\d[\d,]*)")
        for i, l in enumerate(lines):
            if re.search(r"laptop", l, re.IGNORECASE):
                price = None
                # search nearby lines for a price
                for off in range(0, 3):
                    if price:
                        break
                    for idx in (i+off, i-off):
                        if 0 <= idx < len(lines):
                            m = price_re.search(lines[idx])
                            if m:
                                price = m.group(1)
                                break
                items.append((l[:200], price))
                if len(items) >= k * 2:  # gather more, dedup later
                    break
        # dedup by name
        seen = set()
        result: List[Dict[str, Any]] = []
        for name, price in items:
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append({"name": name, "price": price})
            if len(result) >= k:
                break
        return result

class ThreadedBrowserSession:
    """
    A thin proxy that runs all BrowserSession operations on a dedicated worker thread.
    This avoids the "Playwright Sync API inside the asyncio loop" error by ensuring
    every Playwright call happens off the main thread (or any active asyncio loop).
    """

    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="browser-worker")
        self._session: Optional[BrowserSession] = None

    # --- internal helper ---
    def _run(self, method_name: str, *args, **kwargs):
        def task():
            if self._session is None:
                # Create the concrete session inside the worker thread
                self._session = BrowserSession()
            method = getattr(self._session, method_name)
            return method(*args, **kwargs)

        fut = self._executor.submit(task)
        return fut.result()

    # --- public API proxies ---
    def ensure_open(self):
        return self._run("ensure_open")

    def close(self):
        try:
            self._run("close")
        except Exception:
            pass
        try:
            self._executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass

    def apply_script(self, script: List[Dict[str, Any]]) -> str:
        return self._run("apply_script", script)

    def summarize_page(self, max_links: int = 30, max_chars: int = 3000) -> Dict[str, Any]:
        return self._run("summarize_page", max_links, max_chars)

    def extract_text(self) -> str:
        return self._run("extract_text")

    def detect_language(self) -> str:
        return self._run("detect_language")

    def extract_top_k_with_prices(self, k: int = 5) -> List[Dict[str, Any]]:
        return self._run("extract_top_k_with_prices", k)

    def extract_amazon_laptops_top_k(self, k: int = 5, max_price: Optional[float] = None, currency: str = "INR") -> List[Dict[str, Any]]:
        return self._run("extract_amazon_laptops_top_k", k, max_price, currency)
