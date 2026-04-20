STRONG_STACK = ["Python", "FastAPI", "Flask", "Django", "SQLAlchemy", "Redis", "REST API"]
WEAK_STACK = ["Java", "Spring", "Node.js", "Kubernetes", "Terraform"]
DOMAINS = ["AI", "IoT", "센서", "시뮬레이션", "국방", "데이터", "로봇", "방산"]
EXPERIENCE_SCORES = {"신입": 25, "경력무관": 25, "신입~1년": 25, "신입~2년": 25, "신입~3년": 20, "3년 이하": 15}

def calculate_score(job):
    text = f"{job.get('title','')} {job.get('description','')} {job.get('experience','')}".lower()
    stack = min(40, sum(1 for s in STRONG_STACK if s.lower() in text) * 10)
    if any(s.lower() in text for s in WEAK_STACK):
        stack = max(0, stack - 5)
    experience = next((v for k, v in EXPERIENCE_SCORES.items() if k in text), 15)
    domain = min(20, sum(1 for d in DOMAINS if d in text) * 7)
    company = 10
    return min(100, stack + experience + domain + company)
