from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Literal
import asyncio
import json
import time

from Browser.web_erverywhere_browser import WebErverywhereBrowser
from web_erverywhere_agents import stream_task_agent, stream_research_agent, stream_deep_research_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

browser_session: Dict[str, Any] = {"browser": None, "page": None}
browser_events: asyncio.Queue = asyncio.Queue()


class BrowserSetupRequest(BaseModel):
    url: str = "https://www.google.com"


class QueryRequest(BaseModel):
    query: str
    agent_type: Literal["task", "research", "deep_research"]


async def cleanup_browser_session(browser: WebErverywhereBrowser) -> None:
    try:
        if browser:
            await browser.close()
    except Exception:
        pass


@app.post("/setup-browser")
async def setup_browser_endpoint(request: BrowserSetupRequest):
    try:
        if browser_session.get("browser"):
            await cleanup_browser()
        wb = WebErverywhereBrowser()
        browser, context = await wb.connect_to_chrome()
        page = await context.new_page()
        try:
            await page.goto(request.url, timeout=80000, wait_until="domcontentloaded")
        except Exception:
            await page.goto("https://www.google.com", timeout=100000, wait_until="domcontentloaded")

        browser_session.update({"browser": wb, "page": page})
        return {"status": "success", "message": "Browser setup complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup browser: {e}")


@app.post("/cleanup")
async def cleanup_browser():
    try:
        if browser_session.get("browser"):
            await cleanup_browser_session(browser_session["browser"])
        browser_session.update({"browser": None, "page": None})
        return {"status": "success", "message": "Browser cleanup complete"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup browser: {e}")


@app.get("/browser-events")
async def browser_events_endpoint():
    async def event_generator():
        while True:
            try:
                event = await browser_events.get()
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.CancelledError:
                break
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})


async def stream_keepalive_only():
    for _ in range(10):
        yield f"data: {{\n  \"type\": \"keepalive\", \n  \"timestamp\": {time.time()}\n}}\n\n"
        await asyncio.sleep(0.2)
    yield f"data: {{\n  \"type\": \"complete\", \n  \"content\": \"Processing completed\"\n}}\n\n"


@app.post("/query")
async def query_agent(request: QueryRequest):
    if not browser_session.get("page"):
        raise HTTPException(status_code=400, detail="Browser not initialized. Call /setup-browser first")
    if request.agent_type == "task":
        return StreamingResponse(
            stream_task_agent(request.query, browser_session["page"]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Transfer-Encoding": "chunked"},
        )
    if request.agent_type == "research":
        return StreamingResponse(
            stream_research_agent(request.query, browser_session["page"]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Transfer-Encoding": "chunked"},
        )
    if request.agent_type == "deep_research":
        return StreamingResponse(
            stream_deep_research_agent(request.query, browser_session["page"]),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Transfer-Encoding": "chunked"},
        )
    # Fallback keepalive
    return StreamingResponse(stream_keepalive_only(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "Transfer-Encoding": "chunked"})


@app.post("/api/docs/type")
async def type_in_docs(request: Request):
    try:
        if not browser_session.get("page"):
            return JSONResponse(status_code=400, content={"error": "Browser not initialized. Call /setup-browser first"})
        data = await request.json()
        content = data.get("content")
        if not content:
            return JSONResponse(status_code=400, content={"error": "Content is required"})
        page = browser_session["page"]
        await page.goto("https://docs.google.com/document/create")
        await page.wait_for_load_state("domcontentloaded")
        await asyncio.sleep(2)
        editor_selector = ".kix-appview-editor"
        await page.wait_for_selector(editor_selector, timeout=15000)
        editor = await page.query_selector(editor_selector)
        if editor:
            bbox = await editor.bounding_box()
            if bbox:
                x = bbox['x'] + bbox['width'] / 2
                y = bbox['y'] + bbox['height'] / 2
                await page.mouse.click(x, y)
                await asyncio.sleep(1)
                # select all and type
                await page.keyboard.press("Control+A")
                await asyncio.sleep(0.2)
                await page.keyboard.press("Backspace")
                await asyncio.sleep(0.2)
                await page.keyboard.type(content)
                return JSONResponse(status_code=200, content={"message": "Content typed successfully"})
        return JSONResponse(status_code=500, content={"error": "Text editor not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to type content: {e}"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
