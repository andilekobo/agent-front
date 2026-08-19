from rag.chroma_db import get_collection


def retrieve_relevant_knowledge(
    query: str,
    n_results: int = 3
) -> str:
    """
    Retrieve relevant CareerOps knowledge from ChromaDB.
    """

    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]

    if not documents:
        return ""

    return "\n\n".join(
        document.strip()
        for document in documents
    )


# Keep this for direct testing
if __name__ == "__main__":

    query = input("Ask CareerOps: ")

    knowledge = retrieve_relevant_knowledge(query)

    print("\nRelevant knowledge:\n")
    print(knowledge)