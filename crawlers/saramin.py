from playwright.async_api import Browser
from .base import new_context

URL = "https://www.saramin.co.kr/zf_user/search/recruit?searchword=백엔드+python&exp_cd=1&loc_mcd=101000&order=acc_recent&recruitPageCount=20"

async def crawl(browser: Browser) -> list[dict]:
    context = await new_context(browser)
    page = await context.new_page()
    jobs = []
    try:
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("div.item_recruit", timeout=15000)
        cards = await page.query_selector_all("div.item_recruit")
        for card in cards[:20]:
            try:
                title_el = await card.query_selector("a.str_tit")
                company_el = await card.query_selector("strong.corp_name")
                location_el = await card.query_selector("p.work_place")
                date_el = await card.query_selector("span.deadlines")
                posted_el = await card.query_selector("span.date")
                title = await title_el.inner_text() if title_el else ""
                company = await company_el.inner_text() if company_el else ""
                location = await location_el.inner_text() if location_el else ""
                deadline = await date_el.inner_text() if date_el else ""
                posted_at = await posted_el.inner_text() if posted_el else ""
                href = await title_el.get_attribute("href") if title_el else ""
                if not title or not href:
                    continue
                url = f"https://www.saramin.co.kr{href}" if href.startswith("/") else href
                jobs.append({"title": f"{company} - {title}", "url": url, "location": location, "posted_at": posted_at, "deadline": deadline, "description": "", "experience": "", "source": "saramin"})
            except Exception:
                continue
    except Exception as e:
        print(f"[saramin] 오류: {e}")
    finally:
        await context.close()
    return jobs
