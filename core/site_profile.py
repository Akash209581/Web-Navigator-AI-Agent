from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class SiteProfile:
    origin: str
    editor_kind: Optional[str] = None  # 'monaco' | 'cm5' | 'cm6' | 'textarea' | 'contenteditable'
    run_selector: Optional[str] = None
    run_texts: List[str] = field(default_factory=lambda: [
        "Run", "Run Code", "Execute", "Compile", "▶", "Play", "Submit", "Start"
    ])
    output_selectors: List[str] = field(default_factory=lambda: [
        ".output", "#output", "pre.output", "pre", ".terminal", ".console",
        "#console", ".result", "#result", "textarea[readonly]", ".output-window"
    ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origin": self.origin,
            "editor_kind": self.editor_kind,
            "run_selector": self.run_selector,
            "run_texts": self.run_texts,
            "output_selectors": self.output_selectors,
        }

    @staticmethod
    def infer(page) -> "SiteProfile":
        from urllib.parse import urlparse
        url = page.url or "about:blank"
        origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}" if "://" in url else url
        prof = SiteProfile(origin=origin)

        # Detect editor kind
        try:
            if page.locator('.monaco-editor').count() > 0:
                prof.editor_kind = 'monaco'
            elif page.locator('.CodeMirror').count() > 0:
                prof.editor_kind = 'cm5'
            elif page.locator('.cm-editor').count() > 0:
                prof.editor_kind = 'cm6'
            elif page.locator('.ace_editor').count() > 0:
                prof.editor_kind = 'ace'
            elif page.locator('textarea').count() > 0:
                prof.editor_kind = 'textarea'
            elif page.locator('[contenteditable="true"]').count() > 0:
                prof.editor_kind = 'contenteditable'
        except Exception:
            pass

        # Detect run button by common texts
        try:
            # prefer visible button elements
            for txt in [
                "Run Code", "Run", "Execute", "Compile", "▶", "Play", "Submit", "Start"
            ]:
                try:
                    btn = page.get_by_text(txt, exact=False).first
                    if btn and btn.count() > 0:
                        prof.run_selector = None
                        if txt not in prof.run_texts:
                            prof.run_texts.insert(0, txt)
                        break
                except Exception:
                    continue
            # fallback: explicit selectors if any obvious
            if not prof.run_selector:
                for sel in ["button.run", "#run", ".run-btn", "[aria-label='Run']"]:
                    try:
                        if page.locator(sel).count() > 0:
                            prof.run_selector = sel
                            break
                    except Exception:
                        continue
        except Exception:
            pass

        # Filter output selectors to those present on page (keep default as fallback)
        try:
            present = []
            for sel in prof.output_selectors:
                try:
                    if page.locator(sel).count() > 0:
                        present.append(sel)
                except Exception:
                    continue
            if present:
                prof.output_selectors = present
        except Exception:
            pass

        return prof
