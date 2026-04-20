import asyncio
from datetime import date
from playwright.async_api import async_playwright
from crawlers import wanted, jumpit, saramin, jobkorea, rocketpunch
from core.filter import passes_filter
from core.scorer import calculate_score
from core.notion import get_existing_urls, save_jobs, archive_old_jobs

async def run_crawlers():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        tasks = [wanted.crawl(browser), jumpit.crawl(browser), saramin.crawl(browser), jobkorea.crawl(browser), rocketpunch.crawl(browser)]
        crawled = await asyncio.gather(*tasks, return_exceptions=True)
        await browser.close()
    for site_jobs in crawled:
        if isinstance(site_jobs, Exception):
            print(f"크롤러 오류: {site_jobs}")
            continue
        results.extend(site_jobs)
    return results

def main():
    today = date.today().isoformat()
    print(f"\n=== 채용 자동 수집 시작 ({today} KST) ===\n")
    all_jobs = asyncio.run(run_crawlers())
    print(f"수집 원본: {len(all_jobs)}개")
    existing_urls = get_existing_urls()
    print(f"기존 DB URL: {len(existing_urls)}개")
    filtered = []
    for job in all_jobs:
        if job["url"] in existing_urls:
            continue
        if not passes_filter(job):
            continue
        job["score"] = calculate_score(job)
        filtered.append(job)
    seen = set()
    unique = []
    for job in filtered:
        if job["url"] not in seen:
            seen.add(job["url"])
            unique.append(job)
    unique.sort(key=lambda x: x["score"], reverse=True)
    print(f"필터 통과: {len(unique)}개")
    if unique:
        save_jobs(unique)
        print(f"저장 완료: {len(unique)}개")
    else:
        print("저장 대상 없음 (0개도 정상)")
    archived = archive_old_jobs()
    print(f"자동 정리: {archived}개")
    print(f"\n채용 자동 수집 완료 ({today} KST)")
    print(f"신규: {len(unique)}개 / 자동 정리: {archived}개\n")

if __name__ == "__main__":
    main()
