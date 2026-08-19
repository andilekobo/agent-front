import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


def search_jobs(
    query: str,
    location: str,
    results_per_page: int = 10
):
    url = "https://api.adzuna.com/v1/api/jobs/za/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "where": location,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=15)

    response.raise_for_status()

    data = response.json()

    jobs = []

    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "url": job.get("redirect_url"),
        })

    return jobs


def filter_jobs(jobs, query):
    query_lower = query.lower()

    filtered_jobs = []

    # Jobs we don't want for entry-level searches
    excluded_words = [
        "senior",
        "lead",
        "principal",
        "manager",
        "director",
        "head of",
    ]

    for job in jobs:
        title = (job.get("title") or "").lower()
        description = (job.get("description") or "").lower()

        text = f"{title} {description}"

        # Remove senior/management positions
        if any(word in title for word in excluded_words):
            continue

        # Make sure the job is related to the user's search
        query_words = query_lower.split()

        if not any(word in text for word in query_words):
            continue

        filtered_jobs.append(job)

    return filtered_jobs