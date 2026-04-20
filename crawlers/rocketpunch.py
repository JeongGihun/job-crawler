from playwright.async_api import Browser
from .base import new_context

URL = "https://www.rocketpunch.com/jobs?keywords=백엔드+Python&hiring_types=0&location=서울"

async def crawl(browser: Browser) -> list[dict]:
    context = await new_context(browser)
    page = await context.new_page()
    jobs = []
    try:
        await page.goto(URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_selector("div.company-list-item", timeout=15000)
        cards = await page.query_selector_all("div.company-list-item")
        for card in cards[:20]:
            try:
                title_el = await card.query_selector("h4.name a")
                company_el = await card.query_selector("a.company-name")
                location_el = await card.query_selector("span.location")
                date_el = await card.query_selector("span.posted-at")
                title = await title_el.inner_text() if title_el else ""
                company = await company_el.inner_text() if company_el else ""
                location = await location_el.inner_text() if location_el else ""
                posted_at = await date_el.inner_text() if date_el else ""
                href = await title_el.get_attribute("href") if title_el else ""
                if not title or not href:
                    continue
                url = f"https://www.rocketpunch.com{href}" if href.startswith("/") else href
                jobs.append({"title": f"{company} - {title}", "url": url, "location": location, "posted_at": posted_at, "description": "", "experience": "", "deadline": "", "source": "rocketpunch"})
            except Exception:
                continue
    except Exception as e:
        print(f"[rocketpunch] 오류: {e}")
    finally:
        await context.close()
    return jobs
