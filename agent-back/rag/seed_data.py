from rag.chroma_db import get_collection


documents = [
    {
        "id": "python-developer",
        "text": """
        A junior Python developer should understand Python fundamentals,
        functions, classes, modules, error handling, APIs, JSON, SQL,
        Git, and basic software development practices. Familiarity with
        frameworks such as Django or FastAPI is useful.
        """,
        "category": "skills"
    },
    {
        "id": "software-developer",
        "text": """
        A junior software developer should understand programming
        fundamentals, object-oriented programming, databases, REST APIs,
        Git, debugging, testing, and basic software development lifecycle
        concepts. Projects on GitHub can help demonstrate practical ability.
        """,
        "category": "skills"
    },
    {
        "id": "react-developer",
        "text": """
        A junior React developer should understand JavaScript, React
        components, JSX, props, state, hooks, events, API integration,
        React Router, Git, HTML, and CSS. Building practical projects
        is useful for demonstrating frontend development ability.
        """,
        "category": "skills"
    },
    {
        "id": "it-support",
        "text": """
        Entry-level IT support roles commonly require troubleshooting,
        Windows, hardware and software support, networking fundamentals,
        user support, Microsoft 365, ticketing systems, and communication
        skills.
        """,
        "category": "skills"
    },
    {
        "id": "graduate-job-search",
        "text": """
        Graduates looking for their first technology role should consider
        graduate programmes, junior developer positions, IT support roles,
        software engineering roles, internships where appropriate, and
        entry-level technology positions. A portfolio can strengthen an
        application by showing practical projects and technical skills.
        """,
        "category": "career"
    },
    {
        "id": "cv-advice",
        "text": """
        A technology CV should clearly show technical skills, education,
        projects, work experience, certifications, and relevant achievements.
        Projects should describe what was built, the technologies used,
        and the problem solved.
        """,
        "category": "career"
    }
]


collection = get_collection()


collection.upsert(
    ids=[item["id"] for item in documents],
    documents=[item["text"] for item in documents],
    metadatas=[
        {"category": item["category"]}
        for item in documents
    ]
)


print(f"Added {len(documents)} documents to CareerOps RAG.")