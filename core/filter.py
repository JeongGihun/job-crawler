import re
from datetime import date

EXCLUDE_EXPERIENCE = ["3년 이상", "3년+", "4년", "5년+", "5년 이상", "7년", "시니어", "리드", "팀장"]
EXCLUDE_TYPES = ["인턴", "계약직", "프리랜서"]
ALLOWED_LOCATIONS = ["서울", "판교", "수원", "경기"]

def is_excluded_experience(text):
    for keyword in EXCLUDE_EXPERIENCE:
        if keyword in text:
            return True
    if re.search(r"경력\s*[3-9]\d*년\s*이상", text):
        return True
    return False

def is_excluded_type(text):
    return any(k in text for k in EXCLUDE_TYPES)

def is_allowed_location(text):
    return any(loc in text for loc in ALLOWED_LOCATIONS)

def is_expired(deadline_str):
    if not deadline_str:
        return False
    today = date.today()
    try:
        deadline = date.fromisoformat(deadline_str[:10].replace(".", "-"))
        return deadline < today
    except Exception:
        return "마감" in deadline_str or "종료" in deadline_str

def is_fresh(posted_str):
    if not posted_str:
        return False
    if any(k in posted_str for k in ["오늘", "방금", "시간 전", "분 전"]):
        return True
    match = re.search(r"(\d+)일 전", posted_str)
    if match:
        return int(match.group(1)) <= 1
    try:
        posted = date.fromisoformat(posted_str[:10].replace(".", "-"))
        return (date.today() - posted).days <= 1
    except Exception:
        return False

def passes_filter(job):
    text = f"{job.get('title','')} {job.get('description','')} {job.get('experience','')}"
    if is_excluded_experience(text):
        return False
    if is_excluded_type(text):
        return False
    if not is_allowed_location(job.get("location", "")):
        return False
    if is_expired(job.get("deadline", "")):
        return False
    if not is_fresh(job.get("posted_at", "")):
        return False
    return True
