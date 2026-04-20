from playwright.async_api import Browser
from .base import new_context

URL = "https://www.wanted.co.kr/wdlist/518/899?country=kr&job_sort=job.latest_order&years=0&locations=seoul"

async def crawl(browser: Browser) -> list[dict]:
    context = await new_context(browser)
    page = await context.new_page()
    jobs = []
    try:
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("li.JobCard_container__FqChn", timeout=15000)
        cards = await page.query_selector_all("li.JobCard_container__FqChn")
        for card in cards[:20]:
            try:
                title_el = await card.query_selector("strong.JobCard_title__ddkwM")
                company_el = await card.query_selector("span.JobCard_companyName__vZMqJ")
                location_el = await card.query_selector("span.JobCard_location__2EOz0")
                link_el = await card.query_selector("a")
                date_el = await card.query_selector("span.JobCard_date__fHiHp")
                title = await title_el.inner_text() if title_el else ""
                company = await company_el.inner_text() if company_el else ""
                location = await location_el.inner_text() if location_el else ""
                href = await link_el.get_attribute("href") if link_el else ""
                posted_at = await date_el.inner_text() if date_el else ""
                if not title or not href:
                    continue
                url = f"https://www.wanted.co.kr{href}" if href.startswith("/") else href
                jobs.append({"title": f"{company} - {title}", "url": url, "location": location, "posted_at": posted_at, "description": "", "experience": "", "deadline": "", "source": "wanted"})
            except Exception:
                continue
    except Exception as e:
        print(f"[wanted] error: {e}")
    finally:
        await context.close()
    return jobs
