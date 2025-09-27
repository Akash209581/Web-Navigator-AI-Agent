import asyncio
from playwright.async_api import async_playwright
from browser import scrape_text

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # ✅ Make sure to open a real page before scraping
        await page.goto("https://example.com")

        # ✅ Wait for the selector to appear before querying
        await page.wait_for_selector("h1")

        text = await scrape_text(page, "h1")
        print("Scraped:", text)

        await browser.close()

asyncio.run(test())
