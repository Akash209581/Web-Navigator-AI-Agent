import asyncio
import json
from typing import AsyncGenerator, List, Tuple, Optional
from playwright.async_api import Page


async def annotate_all(page: Page):
    # Load marking script
    try:
        with open("marking_scripts/marking.js", "r", encoding="utf-8") as f:
            marking_script = f.read()
        await asyncio.sleep(0.2)
        dom = await page.evaluate(f"""
            (function() {{
                {marking_script}
                return captureInteractiveElements();
            }})()
        """)
        return dom or []
    except Exception:
        return []


async def stream_task_agent(query: str, page: Page) -> AsyncGenerator[str, None]:
    # Step 0: ensure a page
    yield sse({"type": "keepalive", "message": "starting"})

    async def goto_google_if_needed():
        try:
            if "google.com" not in (page.url or ""):
                await page.goto("https://www.google.com", timeout=60000, wait_until="domcontentloaded")
                yield sse({"type": "action", "content": ["Navigated to Google"]})
        except Exception as e:
            yield sse({"type": "error", "content": str(e)})

    # Go to Google first
    async for ev in goto_google_if_needed():
        yield ev

    # Try to type the query
    try:
        await page.wait_for_selector('input[name="q"],textarea[name="q"],#APjFqb', timeout=15000)
        box = await page.query_selector('input[name="q"],textarea[name="q"],#APjFqb')
        if box:
            await box.click()
            await asyncio.sleep(0.1)
            # clear
            await page.keyboard.press("Control+A")
            await asyncio.sleep(0.05)
            await page.keyboard.press("Backspace")
            await asyncio.sleep(0.05)
            await page.keyboard.type(query)
            await asyncio.sleep(0.1)
            await page.keyboard.press("Enter")
            yield sse({"type": "browser_action", "content": [f"Searched for: {query}"]})
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(1.0)
        else:
            yield sse({"type": "error", "content": "Search box not found"})
    except Exception as e:
        yield sse({"type": "error", "content": f"Typing failed: {e}"})

    # Click first result if possible
    try:
        # Google results often:
        # a > h3 or a[data-ved]
        sel = 'a h3'
        await page.wait_for_selector(sel, timeout=15000)
        h3 = await page.query_selector(sel)
        if h3:
            a = await h3.evaluate_handle("e => e.closest('a')")
            if a:
                async with page.context.expect_page(timeout=10000) as new_page_info:
                    await h3.click()
                try:
                    new_page = await new_page_info.value
                    await new_page.bring_to_front()
                    await new_page.wait_for_load_state("domcontentloaded", timeout=20000)
                    yield sse({"type": "browser_action", "content": ["Opened first result in new tab"]})
                except Exception:
                    yield sse({"type": "browser_action", "content": ["Clicked first result (same tab)"]})
        else:
            yield sse({"type": "error", "content": "No results found"})
    except Exception as e:
        yield sse({"type": "error", "content": f"Clicking result failed: {e}"})

    # Annotate and finish
    try:
        dom = await annotate_all(page)
        yield sse({"type": "dom_update", "content": [f"Found {len(dom)} interactive elements"]})
    except Exception:
        pass

    yield sse({"type": "final_response", "content": "Task agent completed initial navigation."})
    yield sse({"type": "complete", "content": "Processing completed"})
    yield sse({"type": "end", "content": "Stream completed"})


# =============== Research Agents ===============
async def search_google(page: Page, query: str) -> AsyncGenerator[str, None]:
    try:
        if "google.com" not in (page.url or ""):
            await page.goto("https://www.google.com", timeout=60000, wait_until="domcontentloaded")
            yield sse({"type": "browser_action", "content": ["Navigated to Google"]})
        await page.wait_for_selector('input[name="q"],textarea[name="q"],#APjFqb', timeout=15000)
        box = await page.query_selector('input[name="q"],textarea[name="q"],#APjFqb')
        if box:
            await box.click()
            await asyncio.sleep(0.05)
            await page.keyboard.press("Control+A")
            await asyncio.sleep(0.02)
            await page.keyboard.press("Backspace")
            await asyncio.sleep(0.02)
            await page.keyboard.type(query)
            await asyncio.sleep(0.05)
            await page.keyboard.press("Enter")
            yield sse({"type": "browser_action", "content": [f"Searched for: {query}"]})
            await page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(0.8)
        else:
            yield sse({"type": "error", "content": "Search box not found"})
    except Exception as e:
        yield sse({"type": "error", "content": f"Search failed: {e}"})


async def collect_top_results(page: Page, max_links: int = 5) -> List[Tuple[str, str]]:
    results: List[Tuple[str, str]] = []
    try:
        await page.wait_for_selector('a h3', timeout=12000)
        items = await page.query_selector_all('a h3')
        for h3 in items[:max_links]:
            try:
                href = await h3.evaluate("e => e.closest('a')?.href || ''")
                title = await h3.evaluate("e => e.textContent?.trim() || ''")
                if href:
                    results.append((title, href))
            except Exception:
                continue
    except Exception:
        pass
    return results


async def fetch_page_summary(page: Page) -> str:
    try:
        # Extract readable text up to a limit
        text = await page.evaluate(
            "() => document.body ? document.body.innerText.slice(0, 4000) : ''"
        )
        return text or ""
    except Exception:
        return ""


def is_pdf_url(url: str) -> bool:
    u = (url or "").lower()
    return u.endswith(".pdf") or "/pdf" in u or "viewer.html" in u


async def stream_research_agent(query: str, page: Page) -> AsyncGenerator[str, None]:
    yield sse({"type": "keepalive", "message": "research-start"})
    async for ev in search_google(page, query):
        yield ev
    links = await collect_top_results(page, max_links=5)
    if not links:
        yield sse({"type": "error", "content": "No results found"})
        yield sse({"type": "complete", "content": "Processing completed"})
        return
    yield sse({"type": "dom_update", "content": [f"Found {len(links)} results"]})

    summaries = []
    for idx, (title, href) in enumerate(links, start=1):
        try:
            new_tab = await page.context.new_page()
            await new_tab.goto(href, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(0.5)
            yield sse({"type": "browser_action", "content": [f"Opened result {idx}: {title}"]})
            if is_pdf_url(new_tab.url):
                summaries.append({"title": title, "url": new_tab.url, "summary": "PDF detected; skipping text extraction."})
            else:
                content = await fetch_page_summary(new_tab)
                summaries.append({"title": title, "url": new_tab.url, "summary": content[:1000]})
            await new_tab.close()
        except Exception as e:
            yield sse({"type": "error", "content": f"Failed to open result {idx}: {e}"})

    yield sse({"type": "final_response", "content": {"query": query, "summaries": summaries}})
    yield sse({"type": "complete", "content": "Processing completed"})
    yield sse({"type": "end", "content": "Stream completed"})


async def stream_deep_research_agent(query: str, page: Page) -> AsyncGenerator[str, None]:
    # Simple deep-research: follow more links, and attempt to gather more context
    yield sse({"type": "keepalive", "message": "deep-research-start"})
    async for ev in search_google(page, query):
        yield ev
    links = await collect_top_results(page, max_links=8)
    if not links:
        yield sse({"type": "error", "content": "No results found"})
        yield sse({"type": "complete", "content": "Processing completed"})
        return
    yield sse({"type": "dom_update", "content": [f"Found {len(links)} results"]})

    compiled: List[dict] = []
    for idx, (title, href) in enumerate(links, start=1):
        try:
            tab = await page.context.new_page()
            await tab.goto(href, timeout=35000, wait_until="domcontentloaded")
            await asyncio.sleep(0.5)
            yield sse({"type": "browser_action", "content": [f"Opened result {idx}: {title}"]})
            if is_pdf_url(tab.url):
                compiled.append({"title": title, "url": tab.url, "chunks": ["PDF detected; skipping text extraction."]})
            else:
                # try to scroll and gather more text
                chunks: List[str] = []
                for _ in range(3):
                    txt = await fetch_page_summary(tab)
                    if txt:
                        chunks.append(txt[:1500])
                    await tab.mouse.wheel(0, 1200)
                    await asyncio.sleep(0.6)
                compiled.append({"title": title, "url": tab.url, "chunks": chunks})
            await tab.close()
        except Exception as e:
            yield sse({"type": "error", "content": f"Failed to open result {idx}: {e}"})

    # naive synthesize
    synthesis = {
        "query": query,
        "sources": [{"title": c["title"], "url": c["url"]} for c in compiled],
        "notes": "Compiled content from multiple sources. For full RAG, integrate embeddings + vector store.",
    }
    yield sse({"type": "final_response", "content": {"synthesis": synthesis, "compiled": compiled}})
    yield sse({"type": "complete", "content": "Processing completed"})
    yield sse({"type": "end", "content": "Stream completed"})


def sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"
