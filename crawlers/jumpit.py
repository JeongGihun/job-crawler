from playwright.async_api import Browser
from .base import new_context

URL = "https://jumpit.saramin.co.kr/positions?sort=createdAt&jobCategory=1&keyword=Python+백엔드"

async def crawl(browser: Browser) -> list[dict]:
    context = await new_context(browser)
    page = await context.new_page()
    jobs = []
    try:
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("div.position_card", timeout=15000)
        cards = await page.query_selector_all("div.position_card")
        for card in cards[:20]:
            try:
                title_el = await card.query_selector("h2.position_card_info_title")
                company_el = await card.query_selector("div.position_card_info_company")
                location_el = await card.query_selector("span.position_card_info_tag")
                link_el = await card.query_selector("a")
                date_el = await card.query_selector("span.position_card_date")
                title = await title_el.inner_text() if title_el else ""
                company = await company_el.inner_text() if company_el else ""
                location = await location_el.inner_text() if location_el else ""
                href = await link_el.get_attribute("href") if link_el else ""
                posted_at = await date_el.inner_text() if date_el else ""
                if not title or not href:
                    continue
                url = f"https://jumpit.saramin.co.kr{href}" if href.startswith("/") else href
                jobs.append({"title": f"{company} - {title}", "url": url, "location": location, "posted_at": posted_at, "description": "", "experience": "", "deadline": "", "source": "jumpit"})
            except Exception:
                continue
    except Exception as e:
        print(f"[jumpit] 오류: {e}")
    finally:
        await context.close()
    return jobs
