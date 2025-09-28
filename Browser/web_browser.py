import asyncio
import platform
from pathlib import Path
from typing import Optional, Tuple
from playwright.async_api import async_playwright, Browser, BrowserContext
import re
import os
import aiohttp
import socket


# Deprecated: use WebErverywhereBrowser in web_erverywhere_browser.py
class WebRoverBrowser:
    def __init__(self, user_data_dir: Optional[str] = None, headless: bool = False, proxy: Optional[str] = None):
        self.base_user_dir = self._default_user_dir()
        self.user_data_dir = user_data_dir
        self.headless = headless
        self.proxy = proxy
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._playwright = None

    def _default_user_dir(self) -> str:
        system = platform.system()
        if system == "Windows":
            return str(Path.home() / "AppData/Local/Google/Chrome/User Data")
        elif system == "Darwin":
            return str(Path.home() / "Library/Application Support/Google/Chrome")
        else:
            return str(Path.home() / ".config/google-chrome")

    async def connect_to_chrome(self, retries: int = 3) -> Tuple[Browser, BrowserContext]:
        self._playwright = await async_playwright().start()

        # Ensure Chrome is launched with remote debugging
        chrome_proc = await self._ensure_chrome_with_rdp()

        # Try to fetch CDP endpoint and connect
        for attempt in range(retries):
            try:
                ws_endpoint = None
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://127.0.0.1:9222/json/version") as resp:
                        data = await resp.json()
                        ws_endpoint = data.get("webSocketDebuggerUrl")
                    if not ws_endpoint:
                        raise RuntimeError("Chrome CDP endpoint not found")
                self._browser = await self._playwright.chromium.connect_over_cdp(ws_endpoint)
                contexts = self._browser.contexts
                if not contexts:
                    self._context = await self._browser.new_context()
                else:
                    self._context = contexts[0]
                return self._browser, self._context
            except Exception:
                if attempt == retries - 1:
                    raise RuntimeError("Failed to connect to Chrome via CDP after retries")
                await asyncio.sleep(2 ** attempt)
        # Should not reach here
        raise RuntimeError("Unexpected connect_to_chrome fallthrough")

    async def _ensure_chrome_with_rdp(self):
        chrome_path = {
            "Windows": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "Linux": "/usr/bin/google-chrome",
        }.get(platform.system())
        cmd = [
            chrome_path,
            "--remote-debugging-port=9222",
            "--no-first-run",
            "--no-default-browser-check",
            "--start-maximized",
        ]
        if self.headless:
            cmd.append("--headless=new")
        # Launch and wait for port to open
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        for _ in range(15):
            await asyncio.sleep(1)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if sock.connect_ex(("127.0.0.1", 9222)) == 0:
                    sock.close()
                    return proc
                sock.close()
            except Exception:
                pass
        return proc

    async def create_context(self) -> BrowserContext:
        if not self._browser:
            raise RuntimeError("Browser not connected")
        if self._context:
            return self._context
        self._context = await self._browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=self._modern_user_agent(),
            locale="en-US",
        )
        await self._add_anti_detection()
        await self._configure_network()
        return self._context

    async def _add_anti_detection(self):
        if not self._context:
            return
        await self._context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US'] });
            window.chrome = { runtime: {} };
            """
        )

    async def _configure_network(self):
        if not self._context:
            return
        await self._context.route("**/*.{png,jpg,jpeg,webp}", lambda route: route.abort())
        await self._context.route(re.compile(r"(analytics|tracking|beacon)"), lambda route: route.abort())

    def _modern_user_agent(self) -> str:
        system = platform.system()
        return f"Mozilla/5.0 ({self._os_info()}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    def _os_info(self) -> str:
        if platform.system() == "Windows":
            return "Windows NT 10.0; Win64; x64"
        elif platform.system() == "Darwin":
            return "Macintosh; Intel Mac OS X 10_15_7"
        return "X11; Linux x86_64"

    async def close(self):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
