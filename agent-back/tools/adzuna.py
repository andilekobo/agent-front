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
    if not ADZUNA_APP_ID:
        raise RuntimeError("ADZUNA_APP_ID is missing from .env")

    if not ADZUNA_APP_KEY:
        raise RuntimeError("ADZUNA_APP_KEY is missing from .env")

    url = "https://api.adzuna.com/v1/api/jobs/za/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "where": location,
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    if response.status_code != 200:
        print("\n[ADZUNA ERROR]")
        print("Status:", response.status_code)
        print("Response:", response.text)

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


def filter_jobs(
    jobs,
    query,
    experience_level="any"
):
    query_lower = query.lower()

    scored_jobs = []

    query_words = [
        word
        for word in query_lower.split()
        if len(word) > 2
    ]

    excluded_words = [
        "senior",
        "lead",
        "principal",
        "manager",
        "director",
        "head of"
    ]

    junior_words = [
        "junior",
        "graduate",
        "entry level",
        "entry-level",
        "trainee"
    ]

    intermediate_words = [
        "intermediate",
        "mid-level",
        "mid level"
    ]

    senior_words = [
        "senior",
        "lead",
        "principal"
    ]

    technologies = [
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "angular",
        "vue",
        "c#",
        ".net",
        "sql",
        "sql server",
        "django",
        "fastapi",
        "node",
        "node.js",
        "php",
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "git"
    ]

    for job in jobs:

        title = (job.get("title") or "").lower()
        description = (job.get("description") or "").lower()
        job_location = (job.get("location") or "").lower()

        text = f"{title} {description}"

        # Remove senior/management jobs
        # when user did not specifically request senior
        if experience_level != "senior":
            if any(word in title for word in excluded_words):
                continue

        score = 0

        # -----------------------------
        # ROLE MATCH
        # -----------------------------

        role_words = [
            word
            for word in query_words
            if word not in [
                "junior",
                "graduate",
                "entry",
                "level",
                "trainee"
            ]
        ]

        for word in role_words:

            if word in title:
                score += 15

            elif word in description:
                score += 7

        # -----------------------------
        # EXPERIENCE MATCH
        # -----------------------------

        if experience_level == "junior":

            if any(word in title for word in junior_words):
                score += 30

            elif any(word in description for word in junior_words):
                score += 15

            if any(word in title for word in intermediate_words):
                score -= 20

        elif experience_level == "intermediate":

            if any(word in title for word in intermediate_words):
                score += 30

            if any(word in title for word in junior_words):
                score -= 10

        elif experience_level == "senior":

            if any(word in title for word in senior_words):
                score += 30

        # -----------------------------
        # LOCATION MATCH
        # -----------------------------

        requested_locations = [
            "johannesburg",
            "pretoria",
            "cape town",
            "durban"
        ]

        for city in requested_locations:

            if city in query_lower:

                if city in job_location:
                    score += 20

                else:
                    score -= 10

        # -----------------------------
        # TECHNOLOGY MATCH
        # -----------------------------

        technology_matches = []

        for technology in technologies:

            if technology in query_lower:

                if technology in text:
                    score += 10
                    technology_matches.append(technology)

        job["matched_skills"] = technology_matches

        # -----------------------------
        # DEVELOPER RELEVANCE
        # -----------------------------

        if "developer" in title:
            score += 10

        if "software developer" in title:
            score += 10

        if "software engineer" in title:
            score += 10

        # -----------------------------
        # EMPLOYMENT TYPE
        # -----------------------------

        if "contract" in title or "contract" in description:
            job["employment_type"] = "Contract"

        elif "permanent" in title or "permanent" in description:
            job["employment_type"] = "Permanent"

        else:
            job["employment_type"] = "Not specified"

        # -----------------------------
        # SALARY
        # -----------------------------

        if job.get("salary_min") or job.get("salary_max"):
            job["salary_available"] = True
        else:
            job["salary_available"] = False

        # -----------------------------
        # MINIMUM RELEVANCE
        # -----------------------------

        if score <= 0:
            continue

        score = max(0, min(score, 100))

        job["match_score"] = score

        scored_jobs.append(job)

    # Best matches first
    scored_jobs.sort(
        key=lambda job: job.get("match_score", 0),
        reverse=True
    )

    return scored_jobs