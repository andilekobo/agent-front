import logging

from dotenv import load_dotenv
from google import genai

from rag.retriever import retrieve_relevant_knowledge
from tools.search_job import search_job


load_dotenv()

logger = logging.getLogger("careerops")

GEMINI_API_KEY = __import__("os").getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=GEMINI_API_KEY)


# --------------------------------------------------
# SIMPLE LOCAL JOB SEARCH EXTRACTION
# No Gemini call here
# --------------------------------------------------

def extract_job_search(message: str):

    text = message.lower()

    # Common IT roles
    roles = [
        "software developer",
        "software engineer",
        "web developer",
        "frontend developer",
        "backend developer",
        "full stack developer",
        "data analyst",
        "data scientist",
        "it support",
        "it technician",
        "systems administrator",
        "network administrator",
        "cybersecurity",
        "devops engineer",
        "cloud engineer",
        "business analyst",
        "database administrator",
    ]

    role = "software developer"

    for possible_role in roles:
        if possible_role in text:
            role = possible_role
            break

    # Location
    locations = [
        "Johannesburg",
        "Pretoria",
        "Cape Town",
        "Durban",
        "Port Elizabeth",
        "East London",
        "Bloemfontein",
        "Midrand",
        "Sandton",
        "Randburg",
        "Roodepoort",
    ]

    location = "Johannesburg"

    for possible_location in locations:
        if possible_location.lower() in text:
            location = possible_location
            break

    return role, location


# --------------------------------------------------
# MAIN CAREEROPS AGENT
# --------------------------------------------------

def talk_to_claude(message: str):

    # -----------------------------
    # 1. RAG RETRIEVAL
    # -----------------------------

    try:

        knowledge = retrieve_relevant_knowledge(message)

        print("\n[RAG] Retrieved knowledge:")
        print(knowledge)

    except Exception as e:

        print(f"[RAG] Retrieval failed: {e}")

        knowledge = ""


    # -----------------------------
    # 2. LOCAL JOB SEARCH EXTRACTION
    # No Gemini call
    # -----------------------------

    jobs = []

    try:

        role, location = extract_job_search(message)

        print(f"\n[JOB SEARCH] Role: {role}")
        print(f"[JOB SEARCH] Location: {location}")

        jobs = search_job(
            role=role,
            location=location
        )

        print(f"[JOB SEARCH] Found {len(jobs)} jobs.")

    except Exception as e:

        print(f"❌ Job search failed: {e}")


    # -----------------------------
    # 3. PREPARE JOB DATA
    # -----------------------------

    job_text = ""

    for index, job in enumerate(jobs[:10], start=1):

        job_text += f"""
Job {index}:
Title: {job.get("title", "Not specified")}
Company: {job.get("company", "Company not listed")}
Location: {job.get("location", "Not specified")}
Salary minimum: {job.get("salary_min", "Not specified")}
Salary maximum: {job.get("salary_max", "Not specified")}
Employment type: {job.get("employment_type", "Not specified")}
Match score: {job.get("match_score", "Not specified")}%
Matched skills: {", ".join(job.get("matched_skills", []))}
Apply URL: {job.get("url", "Not available")}
"""

    if not job_text:
        job_text = "No jobs were found."


    # -----------------------------
    # 4. ONE GEMINI CALL
    # -----------------------------

    prompt = f"""
You are CareerOps, an AI career assistant.

Help the user with career advice and job searching.

USER REQUEST:
{message}

CAREEROPS KNOWLEDGE:
{knowledge}

LIVE ADZUNA JOB RESULTS:
{job_text}

Rules:

- Do not invent jobs.
- Do not invent companies.
- Do not invent salaries.
- Only use the provided job results.
- If no jobs were found, clearly say so.
- Give practical career advice.
- Keep the response concise and useful.
- If the user is just greeting you, respond naturally instead of showing job listings.
- If the user asks for jobs, show the most relevant results.
- Include the application link when available.

Respond naturally as CareerOps.
"""

    print("\n[GEMINI] Generating final response...")

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        answer = response.text

        print("\n[GEMINI] Response generated successfully.")

        return answer

    except Exception as e:

        print(f"\n[GEMINI] Failed: {e}")

        return (
            f"🔎 Found {len(jobs)} jobs for your search.\n\n"
            "CareerOps could not generate the AI response right now.\n"
            f"Error: {e}"
        )