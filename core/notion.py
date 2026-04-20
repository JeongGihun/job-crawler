import os
from datetime import date, timedelta
from notion_client import Client

notion = Client(auth=os.environ["NOTION_API_KEY"])
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

def get_existing_urls():
    urls = set()
    cursor = None
    while True:
        kwargs = {"database_id": DATABASE_ID, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        res = notion.databases.query(**kwargs)
        for page in res["results"]:
            url = page["properties"].get("URL", {}).get("url", "")
            if url:
                urls.add(url)
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    return urls

def save_jobs(jobs):
    today = date.today().isoformat()
    for job in jobs:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "공고 제목": {"title": [{"text": {"content": job["title"]}}]},
                "URL": {"url": job["url"]},
                "적합도 점수": {"number": job["score"]},
                "수집일": {"date": {"start": today}},
                "지원 상태": {"select": {"name": "미검토"}},
            },
        )

def archive_old_jobs():
    cutoff = (date.today() - timedelta(days=30)).isoformat()
    active = {"지원 완료", "서류 통과", "면접 진행", "최종합격"}
    cursor = None
    count = 0
    while True:
        kwargs = {"database_id": DATABASE_ID, "page_size": 100, "filter": {"property": "수집일", "date": {"before": cutoff}}}
        if cursor:
            kwargs["start_cursor"] = cursor
        res = notion.databases.query(**kwargs)
        for page in res["results"]:
            status = (page["properties"].get("지원 상태", {}).get("select") or {}).get("name", "")
            if status not in active:
                notion.pages.update(page_id=page["id"], archived=True)
                count += 1
        if not res.get("has_more"):
            break
        cursor = res.get("next_cursor")
    return count
