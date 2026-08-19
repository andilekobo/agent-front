from tools.adzuna import search_jobs, filter_jobs


def search_job(
    role: str,
    location: str,
    experience_level: str = "any",
    skills=None,
    employment_type: str = "any",
    remote: bool = False,
    min_salary: int = 0
):
    jobs = search_jobs(
        role,
        location
    )

    # Build query for skill matching
    filter_query = role

    if skills:
        if isinstance(skills, list):
            filter_query += " " + " ".join(skills)
        else:
            filter_query += " " + str(skills)

    filtered_jobs = filter_jobs(
        jobs,
        filter_query,
        experience_level
    )

    final_jobs = []

    for job in filtered_jobs:

        # -------------------------
        # Salary filter
        # -------------------------

        salary_min = job.get("salary_min") or 0
        salary_max = job.get("salary_max") or 0

        if min_salary > 0:

            highest_salary = max(
                salary_min,
                salary_max
            )

            if highest_salary < min_salary:
                continue

        # -------------------------
        # Employment type filter
        # -------------------------

        if employment_type != "any":

            job_type = job.get(
                "employment_type",
                "Not specified"
            ).lower()

            if employment_type.lower() not in job_type:
                continue

        # -------------------------
        # Remote filter
        # -------------------------

        if remote:

            title = (
                job.get("title") or ""
            ).lower()

            description = (
                job.get("description") or ""
            ).lower()

            text = f"{title} {description}"

            remote_words = [
                "remote",
                "work from home",
                "working from home",
                "hybrid"
            ]

            if not any(
                word in text
                for word in remote_words
            ):
                continue

        final_jobs.append(job)

    return final_jobs