from tools.adzuna import search_jobs

jobs = search_jobs(
    query="Software Developer",
    location="Johannesburg",
    results_per_page=5
)

print(f"\nFound {len(jobs)} jobs:\n")

for job in jobs:
    print("TITLE:", job["title"])
    print("COMPANY:", job["company"])
    print("LOCATION:", job["location"])
    print("URL:", job["url"])
    print("-" * 60)