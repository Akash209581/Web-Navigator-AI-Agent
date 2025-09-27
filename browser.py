from playwright.async_api import Page

async def navigate_to_url(page: Page, url: str):
    await page.goto(url, timeout=60000)

async def click_element(page: Page, css_selector: str):
    await page.click(css_selector)

async def type_text(page: Page, css_selector: str, text: str):
    await page.fill(css_selector, text)

async def scrape_text(page: Page, css_selector: str):
    elements = await page.query_selector_all(css_selector)
    return [await e.text_content() for e in elements]
